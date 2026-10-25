import json
from app.normalizer.aws import aws_normalizer

# Representative AWS CloudTrail fixture used in test_run_instances
raw_log = {
    "provider": "AWS",
    "eventName": "RunInstances",
    "eventSource": "ec2.amazonaws.com",
    "eventTime": "2026-09-04T07:00:00Z",
    "awsRegion": "ap-south-1",
    "sourceIPAddress": "1.2.3.4",
    "userIdentity": {
        "userName": "devops"
    }
}

# Execute the actual normalizer method
normalized = aws_normalizer.normalize(raw_log)

print("================ RAW AWS EVENT ================")
print(json.dumps(raw_log, indent=2))

print("\n================ NORMALIZED OUTPUT ================")
print(json.dumps(normalized, indent=2))

print("\n================ IMPORTANT MAPPINGS ================")
print(f"provider:     {raw_log.get('provider')} -> {normalized.get('provider')}")
print(f"username:     {raw_log.get('userIdentity', {}).get('userName')} -> {normalized.get('username')}")
print(f"event_name:   {raw_log.get('eventName')} -> {normalized.get('event_name')}")
print(f"event_type:   (classified from {raw_log.get('eventSource')} + {raw_log.get('eventName')}) -> {normalized.get('event_type')}")
print(f"resource:     {raw_log.get('resources')} -> {normalized.get('resource')}")
print(f"source_ip:    {raw_log.get('sourceIPAddress')} -> {normalized.get('source_ip')}")
print(f"region:       {raw_log.get('awsRegion')} -> {normalized.get('region')}")
print(f"event_time:   {raw_log.get('eventTime')} -> {normalized.get('event_time')}")
print(f"raw_log:      preserved sanitized dictionary -> {type(normalized.get('raw_log')).__name__}")

print("\n================ RESULT ================")
print("AWS normalization completed successfully.")
