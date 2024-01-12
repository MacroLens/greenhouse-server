# Terraform configuration to set up providers by version.
terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.1"
    }
  }
}

# Configures the provider to use the resource block's specified project for quota checks.
provider "google-beta" {
  user_project_override = true
}

# Configures the provider to not use the resource block's specified project for quota checks.
# This provider should only be used during project creation and initializing services.
provider "google-beta" {
  alias = "no_user_project_override"
  user_project_override = false
}

data "google_billing_account" "acct" {
  display_name = "My Billing Account"
  open         = true
}

# Creates a new Google Cloud project.
resource "google_project" "default" {
  provider   = google-beta.no_user_project_override

  name       = "Project Greenhouse"
  project_id = "greenhouse-infrastructure-${random_string.project-suffix.result}"
  # Required for any service that requires the Blaze pricing plan
  # (like Firebase Authentication with GCIP)
  billing_account = data.google_billing_account.acct.id

  # Required for the project to display in any list of Firebase projects.
  labels = {
    "firebase" = "enabled"
  }
}

# Enables required APIs.
resource "google_project_service" "default" {
  provider = google-beta.no_user_project_override
  project  = google_project.default.project_id
  for_each = toset([
    "cloudbilling.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudfunctions.googleapis.com",
    "eventarc.googleapis.com",
    "run.googleapis.com",
    # "cloudresourcemanager.googleapis.com",
    "firebase.googleapis.com",
    "firestore.googleapis.com",
    "firebaserules.googleapis.com",
    # Enabling the ServiceUsage API allows the new project to be quota checked from now on.
    # "serviceusage.googleapis.com",
  ])
  service = each.key

  # Don't disable the service if the resource block is removed by accident.
  # disable_on_destroy = false
  disable_dependent_services = true
}

# Enables Firebase services for the new project created above.
resource "google_firebase_project" "default" {
  provider = google-beta
  project  = google_project.default.project_id

  # Waits for the required APIs to be enabled.
  depends_on = [
    google_project_service.default,
  ]
}

# Get the SDK service account name.
data "external" "firebase_service_account" {
  program = ["bash", "${path.module}/get_service_account.sh"] 
  query = {
    project_id = google_project.default.project_id
  }
  depends_on = [ 
    google_firebase_project.default,
  ]
}

# Create a key for the service account sdk to use.
resource "google_service_account_key" "serviceKey" {
  # Use the data to ensure the account is consistent.
  service_account_id = data.external.firebase_service_account.result.email
}

# Creates a Firebase Android App in the new project created above.
resource "google_firebase_android_app" "default" {
  provider = google-beta

  project      = google_project.default.project_id
  display_name = "Greenhouse Monitor"
  package_name = "com.example.greenhousemonitor"

  # Wait for Firebase to be enabled in the Google Cloud project before creating this App.
  depends_on = [
    google_firebase_project.default,
  ]
}

data "google_firebase_android_app_config" "app_config" {
  provider = google-beta

  app_id = google_firebase_android_app.default.app_id
  project = google_project.default.project_id
}


# Create the backend database.
resource "google_firestore_database" "database" {
  provider = google-beta

  project                 = google_project.default.project_id
  name                    = "(default)"
  location_id             = "nam5"
  type                    = "FIRESTORE_NATIVE"
  # If you do not want to delete the database when running `terraform destroy`
  # switch to "DELETE_PROTECTION_ENABLED"
  delete_protection_state = "DELETE_PROTECTION_DISABLED"
  deletion_policy         = "DELETE"
  depends_on = [
    google_firebase_project.default,
  ]
}

# Create a TTL policy on collection
resource "google_firestore_field" "timestamp" {
  provider = google-beta

  project = google_project.default.project_id
  collection = "sensor-data"
  field = "ttl"

  # enables a TTL policy for the document based on the value of entries with this field
  ttl_config {}

  # Disable all single field indexes for the timestamp property.
  index_config {}
  depends_on = [ 
    google_firestore_database.database,
  ]
}

# Create a TTL policy on collection
resource "google_firestore_field" "dates_timestamp" {
  provider = google-beta

  project = google_project.default.project_id
  collection = "dates"
  field = "ttl"

  # enables a TTL policy for the document based on the value of entries with this field
  ttl_config {}

  # Disable all single field indexes for the timestamp property.
  index_config {}
  depends_on = [ 
    google_firestore_database.database,
  ]
}


resource "google_firebaserules_release" "primary" {
  provider = google-beta
  name         = "cloud.firestore"
  ruleset_name = google_firebaserules_ruleset.firestore.name
  project = google_firebase_project.default.project

  
  lifecycle {
    replace_triggered_by = [
      google_firebaserules_ruleset.firestore
    ]
  }
}

resource "google_firebaserules_ruleset" "firestore" {
  provider = google-beta
  project = google_firebase_project.default.project
  source {
    files {
      content = <<-EOT
service cloud.firestore {
  match /databases/{database}/documents {
    match /sensor-data/{data_entry} {
      allow read
      allow write: if false;

    }
    match /sensor-aggregate/{aggregate=**} {
      allow read
      allow write: if false;
    }
  }
}
EOT
      name    = "firestore.rules"
    }
  }
}

data "google_service_account" "firebase-admin" {
  project = google_project.default.project_id
  account_id = data.external.firebase_service_account.result.email
}

resource "google_project_iam_binding" "admin-account-iam" {
  project = google_project.default.project_id
  role               = "roles/eventarc.eventReceiver"
  members = [
    data.google_service_account.firebase-admin.member
  ]
}
resource "google_project_iam_binding" "admin-account-log" {
  project = google_project.default.project_id
  role               = "roles/logging.logWriter"
  members = [
    data.google_service_account.firebase-admin.member
  ]
}
resource "google_project_iam_binding" "admin-account-invoker" {
  project = google_project.default.project_id
  role               = "roles/run.invoker"
  members = [
    data.google_service_account.firebase-admin.member
  ]
}


resource "google_storage_bucket" "bucket" {
  project = google_project.default.project_id

  name     = "code-bucket-${random_string.project-suffix.result}"
  location = "us-west1"

  force_destroy = true
}

resource "google_storage_bucket_object" "archive" {
  name   = "index_${lower(replace(base64encode(data.archive_file.archive_aggregate_code.output_md5), "=", ""))}.zip"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.archive_aggregate_code.output_path

  depends_on = [ 
    data.archive_file.archive_aggregate_code,
    google_storage_bucket.bucket
  ]
}

data "archive_file" "archive_aggregate_code" {
  type        = "zip"
  source_dir  = "cloud-function"
  output_path = "artifacts/index.zip"
}

resource "google_cloudfunctions2_function" "aggregator-function" {
  project = google_project.default.project_id
  location = "us-west1"

  name = "aggregator-${random_string.project-suffix.result}"

  description = "Aggregator of stats per day."
  build_config {
    runtime = "python311"
    entry_point = "myfunction"
    source {
      storage_source {
        bucket = google_storage_bucket.bucket.name
        object = google_storage_bucket_object.archive.name
      }
    }
  }
  service_config {
    max_instance_count  = 1
    available_memory    = "128Mi"
    service_account_email = data.external.firebase_service_account.result.email
    environment_variables = {
      # All timezones the backend will support as UTC offsets.
      TIMEZONES = "[-12, -11, -10, -9, -8, -7, -6, -5, -4, 10, 12]"
    }
  }
  event_trigger {
    event_type = "google.cloud.firestore.document.v1.created"
    trigger_region = google_firestore_database.database.location_id
    # resource = google_firestore_database.database.id
    service_account_email = data.external.firebase_service_account.result.email
    event_filters {
      attribute = "database"
      value = "(default)"
    }
    event_filters {
      attribute = "document"
      value = "sensor-data/{dataentry}"
      operator = "match-path-pattern"
    }
  }

  depends_on = [ 
    google_storage_bucket_object.archive,
    google_project_iam_binding.admin-account-iam,
    google_project_iam_binding.admin-account-log,
    google_project_iam_binding.admin-account-invoker,
  ]
}

# Random project suffix for easy destroy.
resource "random_string" "project-suffix" {
  length  = 4
  upper = false
  special = false
}

output "service-certificate" {
  value     = base64decode(google_service_account_key.serviceKey.private_key)
  sensitive = true
}

output "google-services" {
  value = base64decode(data.google_firebase_android_app_config.app_config.config_file_contents)
  sensitive = true
}