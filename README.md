# Greenhouse Monitor Server
Uploads data to Firebase for use with the greenhouse-monitor app.

## Requirements:
sense_hat
numpy
google-cloud-firestore
firebase_admin
grpcio-status==1.59.0
grpcio==1.59.0

## Cloud certificates
After setting up the firebase app you will need a certificate
to authenticate and modify the database in firestore.

1. Go to your [GCC service accounts](https://console.cloud.google.com/iam-admin/serviceaccounts).
2. Select your firebase project.
3. Under "Service accounts for project (PROJECT NAME)" click on the three dots under the
"actions" column > "manage keys"
4. Click "Add Key" > "Create new key" > JSON > CREATE
5. Download the key to the Pi as `cert.json`. **Do not commit this private key to VCS**

## Setup TTL for Database
After installing [gcloud](https://cloud.google.com/sdk/docs/install#deb) to your Pi, you
need to now setup a time to live policy on firestore. 

## Google Cloud Billing
Enable billing for google cloud, you won't likely be charged for anything, this
is to make Time to Live setup on the firestore database. See this [resource](https://cloud.google.com/billing/docs/how-to/create-billing-account).

## Terraform
Install gcloud, terraform.

Run 
```
gcloud auth application-default login
```
To authenticate with google cloud using your account.

Then run the following terraform commands to spin up the database and android app.
```
terraform init -upgrade
terraform apply
```

Extract the certificate from the state
```
terraform output -raw service-certificate > cert.json
```

Extract the json for android studio from the state and follow this [guide](https://firebase.google.com/docs/android/setup#add-config-file). Or just add it to the root module folder your app,
and [use the assistant in Android Studio](https://firebase.google.com/docs/android/setup#assistant).
```
terraform output -raw google-services > google-services.json
```

To clean up
```
terraform destroy
```
