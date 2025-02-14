#!/bin/bash

# Exit if any of the intermediate steps fail
set -e

# Load the project id
eval "$(jq -r '@sh "PROJECT_ID=\(.project_id)"')"

# Sleep to wait for the service-account to propogate
marker_file=".setup_marker"
# Check if the marker file exists
if [ ! -f "$marker_file" ]; then
    sleep 60  # Sleep longer for the first run
    touch "$marker_file"  # Create marker file
else
    sleep 5
fi

# Execute gcloud command to list service account emails
EMAIL=$(gcloud iam service-accounts list \
    --project=${PROJECT_ID} \
    --filter='displayName=firebase-adminsdk' \
    --format='value(email)' \
    --verbosity=error )

# Output the result to stdout
if [[ -z "$EMAIL" ]]; then
    echo "no service account found from gcloud" 1>&2
    exit 1
else
    jq -n --arg email "$EMAIL" '{"email": $email}'
fi
