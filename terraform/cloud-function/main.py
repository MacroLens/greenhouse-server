from cloudevents.http import CloudEvent
import functions_framework
from google.cloud import firestore
from google.events.cloud import firestore as firestoredata
from datetime import datetime, timedelta, timezone
import os
import json

client = firestore.Client()
TIMEZONES = json.loads(os.environ.get("TIMEZONES", "Environment Variable not set."))
print(TIMEZONES)

# Takes environment variables that say what timezones to consider.
@functions_framework.cloud_event
def myfunction(cloud_event: CloudEvent) -> None:
    """Triggers by a change to a Firestore document.

    Args:
        cloud_event: cloud event with information on the firestore event trigger
    """
    firestore_payload = firestoredata.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)

    # Get the collection name and the document name.
    path_parts = firestore_payload.value.name.split("/")
    separator_idx = path_parts.index("documents")
    collection_path = path_parts[separator_idx + 1]
    document_path = "/".join(path_parts[(separator_idx + 2) :])

    print(f"Collection path: {collection_path}")
    print(f"Document path: {document_path}")

    print(f"Function triggered by change to: {cloud_event['source']}")
    # print(firestore_payload.value)
    payload_time = firestore_payload.value.fields["timestamp"].timestamp_value
    payload_temperature = float(firestore_payload.value.fields["temperature"].double_value) # float
    payload_pressure = int(firestore_payload.value.fields["pressure"].integer_value) # int
    payload_humidity = float(firestore_payload.value.fields["humidity"].double_value) # float

    print("Current time from value: ",payload_time.isoformat())
    for tz in TIMEZONES:
        utc_offset_time = payload_time.astimezone(timezone(timedelta(hours=tz)))
        aggregate_doc_ref = client.collection(f"sensor-aggregate/UTC{tz}/dates").document(f"{utc_offset_time.strftime('%Y-%m-%d')}")
        aggregate_doc = aggregate_doc_ref.get()
        if aggregate_doc.exists:
            aggregate_dict = aggregate_doc.to_dict()
            if payload_temperature >= aggregate_dict["hi-temperature"]:
                aggregate_doc_ref.set({
                    "hi-timestamp": payload_time, 
                    "hi-temperature": payload_temperature,
                }, merge=True)
            if payload_temperature <= aggregate_dict["lo-temperature"]:
                aggregate_doc_ref.set({
                    "lo-timestamp": payload_time, 
                    "lo-temperature": payload_temperature,
                }, merge=True)

        else:
            aggregate_doc_ref.set({
                "hi-timestamp": payload_time, 
                "hi-temperature": payload_temperature,
                "lo-timestamp": payload_time, 
                "lo-temperature": payload_temperature,
                "ttl": payload_time.astimezone() + timedelta(days=365*10)
            })
        
    # print(firestore_payload.value.fields["timestamp"].timestamp_value)