import json
from app.normalizer.gcp import gcp_normalizer

# Exact GCP fixture from test_audit_log() in test_gcp_normalizer.py
raw_log = {
    "provider": "GCP",
    "timestamp": "2026-07-27T12:00:00Z",
    "protoPayload": {
        "authenticationInfo": {
            "principalEmail": "krish@gmail.com"
        },
        "methodName": "storage.objects.get"
    }
}

# Call the actual GCP normalizer method
normalized = gcp_normalizer.normalize(raw_log)

print("================ RAW GCP EVENT ================\n")
print(json.dumps(raw_log, indent=2))

print("\n================ ACTUAL GCP NORMALIZED OUTPUT ================\n")
print(json.dumps(normalized, indent=2))

print("\n================ IMPORTANT MAPPINGS ================\n")
print(f"provider:    {raw_log.get('provider')} -> {normalized.get('provider')}")
print(f"username:    {raw_log.get('protoPayload', {}).get('authenticationInfo', {}).get('principalEmail')} -> {normalized.get('username')}")
print(f"event_name:  {raw_log.get('protoPayload', {}).get('methodName')} -> {normalized.get('event_name')}")
print(f"event_type:  (classified from '{normalized.get('event_name')}') -> {normalized.get('event_type')}")
print(f"resource:    {raw_log.get('protoPayload', {}).get('resourceName')} -> {normalized.get('resource')}")
print(f"source_ip:   {raw_log.get('protoPayload', {}).get('callerIp')} -> {normalized.get('source_ip')}")
print(f"region:      {raw_log.get('resourceLocation')} -> {normalized.get('region')}")
print(f"event_time:  {raw_log.get('timestamp')} -> {normalized.get('event_time')}")
print(f"raw_log:     preserved original dictionary -> {type(normalized.get('raw_log')).__name__}")
