import pytest
from app.utils.redaction import redact_sensitive_data, REDACTED_MARKER

def test_redact_top_level_dict():
    raw_event = {
        "eventName": "ConsoleLogin",
        "accessKeyId": "TEST_ACCESS_KEY",
        "secretAccessKey": "TEST_SECRET_KEY"
    }
    
    redacted = redact_sensitive_data(raw_event)
    
    assert redacted["eventName"] == "ConsoleLogin"
    assert redacted["accessKeyId"] == REDACTED_MARKER
    assert redacted["secretAccessKey"] == REDACTED_MARKER

def test_redact_nested_dict():
    raw_event = {
        "userIdentity": {
            "type": "IAMUser",
            "credentials": {
                "accessKeyId": "TEST_ACCESS_KEY",
                "sessionToken": "TEST_SESSION_TOKEN"
            }
        },
        "eventSource": "sts.amazonaws.com"
    }
    
    redacted = redact_sensitive_data(raw_event)
    
    assert redacted["eventSource"] == "sts.amazonaws.com"
    assert redacted["userIdentity"]["type"] == "IAMUser"
    assert redacted["userIdentity"]["credentials"] == REDACTED_MARKER

def test_redact_lists_and_nested_objects():
    raw_event = {
        "items": [
            {"password": "TEST_PASSWORD"},
            {"clientSecret": "TEST_SECRET"},
            "primitive_in_list",
            {"authorization": "TEST_AUTH"}
        ]
    }
    
    redacted = redact_sensitive_data(raw_event)
    
    assert redacted["items"][0]["password"] == REDACTED_MARKER
    assert redacted["items"][1]["clientSecret"] == REDACTED_MARKER
    assert redacted["items"][2] == "primitive_in_list"
    assert redacted["items"][3]["authorization"] == REDACTED_MARKER

def test_forensic_fields_remain_unchanged():
    raw_event = {
        "userIdentity": {
            "arn": "arn:aws:iam::123456789012:role/MyRole",
            "userName": "testuser"
        },
        "roleArn": "arn:aws:iam::123456789012:role/MyRole",
        "requestID": "12345-abcde",
        "eventID": "abcde-12345"
    }
    
    redacted = redact_sensitive_data(raw_event)
    
    # Asserting these fields are NOT redacted
    assert redacted["userIdentity"]["arn"] == "arn:aws:iam::123456789012:role/MyRole"
    assert redacted["userIdentity"]["userName"] == "testuser"
    assert redacted["roleArn"] == "arn:aws:iam::123456789012:role/MyRole"

def test_original_object_not_mutated():
    raw_event = {
        "accessKeyId": "TEST_ACCESS_KEY"
    }
    
    redacted = redact_sensitive_data(raw_event)
    
    assert redacted["accessKeyId"] == REDACTED_MARKER
    assert raw_event["accessKeyId"] == "TEST_ACCESS_KEY"

def test_safely_handles_edge_cases():
    assert redact_sensitive_data(None) is None
    assert redact_sensitive_data({}) == {}
    assert redact_sensitive_data([]) == []
    assert redact_sensitive_data("primitive string") == "primitive string"
    assert redact_sensitive_data(12345) == 12345
