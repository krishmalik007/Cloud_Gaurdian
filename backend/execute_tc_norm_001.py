import json
from app.normalizer.aws import aws_normalizer


def run_tc_norm_001():
    print("=" * 80)
    print("=== TC-NORM-001: AWS CloudTrail Normalization Test ===")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # 1. Representative Raw AWS CloudTrail Event Fixture
    # --------------------------------------------------------------------------
    raw_cloudtrail_event = {
        "eventVersion": "1.11",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAEXAMPLE567890123",
            "arn": "arn:aws:iam::195236889241:user/security-analyst",
            "accountId": "195236889241",
            "userName": "security-analyst"
        },
        "eventTime": "2026-10-08T07:45:00Z",
        "eventSource": "ec2.amazonaws.com",
        "eventName": "RunInstances",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "198.51.100.42",
        "userAgent": "aws-cli/2.15.0 Python/3.11.6 Windows/10",
        "requestParameters": {
            "instancesSet": {
                "items": [
                    {
                        "imageId": "ami-0abcdef1234567890",
                        "minCount": 1,
                        "maxCount": 1,
                        "keyName": "prod-ssh-key",
                        "instanceType": "t3.large"
                    }
                ]
            }
        },
        "responseElements": {
            "instancesSet": {
                "items": [
                    {
                        "instanceId": "i-0123456789abcdef0",
                        "currentState": {"code": 0, "name": "pending"}
                    }
                ]
            }
        },
        "requestID": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
        "eventID": "f1e2d3c4-b5a6-7890-1234-56789abcdef0",
        "readOnly": False,
        "resources": [
            {
                "accountId": "195236889241",
                "type": "AWS::EC2::Instance",
                "ARN": "arn:aws:ec2:ap-south-1:195236889241:instance/i-0123456789abcdef0"
            }
        ],
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }

    print("\n--- [A] RAW AWS CLOUDTRAIL EVENT INPUT ---")
    print(json.dumps(raw_cloudtrail_event, indent=2))

    # --------------------------------------------------------------------------
    # 2. Execute AWS Normalization
    # --------------------------------------------------------------------------
    normalized_event = aws_normalizer.normalize(raw_cloudtrail_event)

    print("\n--- [B] NORMALIZED CLOUDGUARDIAN COMMON EVENT OUTPUT ---")
    print(json.dumps(normalized_event, indent=2))

    # --------------------------------------------------------------------------
    # 3. Field Mapping & Preservation Verification
    # --------------------------------------------------------------------------
    print("\n--- [C] FIELD MAPPING & INTEGRITY VERIFICATION ---")
    mappings = [
        ("provider", raw_cloudtrail_event["provider"], normalized_event["provider"]),
        ("username (from userIdentity.userName)", raw_cloudtrail_event["userIdentity"]["userName"], normalized_event["username"]),
        ("event_name (from eventName)", raw_cloudtrail_event["eventName"], normalized_event["event_name"]),
        ("event_type (classified from ec2 + RunInstances)", "COMPUTE", normalized_event["event_type"]),
        ("resource (from resources[0].ARN)", raw_cloudtrail_event["resources"][0]["ARN"], normalized_event["resource"]),
        ("source_ip (from sourceIPAddress)", raw_cloudtrail_event["sourceIPAddress"], normalized_event["source_ip"]),
        ("region (from awsRegion)", raw_cloudtrail_event["awsRegion"], normalized_event["region"]),
        ("event_time (from eventTime)", raw_cloudtrail_event["eventTime"], normalized_event["event_time"]),
    ]

    all_passed = True
    for field_desc, raw_val, norm_val in mappings:
        match = (norm_val == raw_val)
        status = "[MATCH]" if match else "[MISMATCH]"
        if not match:
            all_passed = False
        print(f"  {status:10} {field_desc:45} -> Normalized: '{norm_val}'")

    # Verify underlying raw_log integrity & preservation of metadata
    raw_preserved = normalized_event.get("raw_log", {})
    assert raw_preserved["readOnly"] == raw_cloudtrail_event["readOnly"]
    assert raw_preserved["eventType"] == raw_cloudtrail_event["eventType"]
    assert raw_preserved["managementEvent"] == raw_cloudtrail_event["managementEvent"]
    assert raw_preserved["recipientAccountId"] == raw_cloudtrail_event["recipientAccountId"]
    assert "requestParameters" in raw_preserved
    assert "responseElements" in raw_preserved
    print("  [MATCH]    raw_log (preserves readOnly, eventType, managementEvent, recipientAccountId, request/response)")

    print("\n" + "=" * 80)
    if all_passed:
        print("RESULT: PASS — Common representation produced without required-field loss.")
    else:
        print("RESULT: FAIL — Field mapping mismatch detected.")
    print("=" * 80)


if __name__ == "__main__":
    run_tc_norm_001()
