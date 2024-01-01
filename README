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
