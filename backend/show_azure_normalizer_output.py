import json
from app.normalizer.azure import azure_normalizer

# Exact Azure fixture from test_activity_log() in test_azure_normalizer.py
raw_log = {
    "provider": "AZURE",
    "caller": "krish",
    "operationName": {
        "value": "Create VM"
    },
    "callerIpAddress": "20.10.10.10",
    "resourceLocation": "Central India",
    "eventTimestamp": "2026-07-27T12:00:00Z"
}

# Call the actual normalizer method
normalized = azure_normalizer.normalize(raw_log)

print("================ RAW AZURE EVENT ================\n")
print(json.dumps(raw_log, indent=2))

print("\n================ ACTUAL AZURE NORMALIZED OUTPUT ================\n")
print(json.dumps(normalized, indent=2))

print("\n================ IMPORTANT MAPPINGS ================\n")
print(f"provider:    {raw_log.get('provider')} -> {normalized.get('provider')}")
print(f"username:    {raw_log.get('caller')} -> {normalized.get('username')}")
print(f"event_name:  {raw_log.get('operationName', {}).get('value')} -> {normalized.get('event_name')}")
print(f"event_type:  (classified from '{normalized.get('event_name')}') -> {normalized.get('event_type')}")
print(f"resource:    {raw_log.get('resourceId')} -> {normalized.get('resource')}")
print(f"source_ip:   {raw_log.get('callerIpAddress')} -> {normalized.get('source_ip')}")
print(f"region:      {raw_log.get('resourceLocation')} -> {normalized.get('region')}")
print(f"event_time:  {raw_log.get('eventTimestamp')} -> {normalized.get('event_time')}")
print(f"raw_log:     preserved original dictionary -> {type(normalized.get('raw_log')).__name__}")
