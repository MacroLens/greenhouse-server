# Greenhouse Monitor Server
Uploads data to Firebase for use with the greenhouse-monitor app.

## Requirements:
On the Pi running Bullseye
```
sudo apt install sense-hat git
pip install firebase_admin numpy
```

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
