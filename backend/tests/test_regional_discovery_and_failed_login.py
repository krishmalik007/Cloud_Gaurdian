from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from app.correlation.rules.authentication_rules import (
    _parse_event_timestamp,
    check_multiple_failed_logins,
)
from app.normalizer.aws import aws_normalizer
from app.pipeline.incident_pipeline import incident_pipeline
from app.services.cloudtrail_s3_service import CloudTrailS3IngestionService
from app.storage.event_repository import EventRepository
from app.storage.incident_repository import IncidentRepository


# ==============================================================================
# 1. Regional Discovery & S3 Key Region Extraction Tests
# ==============================================================================

def test_extract_region_from_key():
    """Verify region extraction from various CloudTrail S3 key structures."""
    key_stockholm = (
        "AWSLogs/195236889241/CloudTrail/eu-north-1/2026/10/20/"
        "195236889241_CloudTrail_eu-north-1_20261020T0910Z_N5OxZBYhtsu7Meqd.json.gz"
    )
    assert CloudTrailS3IngestionService._extract_region_from_key(key_stockholm) == "eu-north-1"

    key_mumbai = (
        "AWSLogs/195236889241/CloudTrail/ap-south-1/2026/10/20/"
        "195236889241_CloudTrail_ap-south-1_20261020T0910Z_abcd1234efgh5678.json.gz"
    )
    assert CloudTrailS3IngestionService._extract_region_from_key(key_mumbai) == "ap-south-1"

    key_virginia = (
        "AWSLogs/195236889241/CloudTrail/us-east-1/2026/10/20/"
        "195236889241_CloudTrail_us-east-1_20261020T0910Z_xyz9876543210000.json.gz"
    )
    assert CloudTrailS3IngestionService._extract_region_from_key(key_virginia) == "us-east-1"

    # Non-CloudTrail or invalid keys return None
    assert CloudTrailS3IngestionService._extract_region_from_key("") is None
    assert CloudTrailS3IngestionService._extract_region_from_key("other/path/file.json.gz") is None


def test_discover_regions_via_common_prefixes():
    """Verify dynamic discovery of regional directories using S3 delimiter."""
    mock_s3 = MagicMock()
    mock_paginator = MagicMock()
    mock_s3.get_paginator.return_value = mock_paginator
    mock_paginator.paginate.return_value = [
        {
            "CommonPrefixes": [
                {"Prefix": "AWSLogs/195236889241/CloudTrail/ap-south-1/"},
                {"Prefix": "AWSLogs/195236889241/CloudTrail/eu-north-1/"},
                {"Prefix": "AWSLogs/195236889241/CloudTrail/us-east-1/"},
            ]
        }
    ]

    service = CloudTrailS3IngestionService(s3_client=mock_s3)
    regions = service.discover_regions(
        bucket="test-bucket",
        prefix="AWSLogs/195236889241/CloudTrail/"
    )

    assert "eu-north-1" in regions
    assert "ap-south-1" in regions
    assert "us-east-1" in regions
    assert regions == ["ap-south-1", "eu-north-1", "us-east-1"]


def test_discover_objects_multi_region_preservation():
    """Verify _discover_objects returns objects across all regions chronologically."""
    mock_s3 = MagicMock()
    mock_paginator = MagicMock()
    mock_s3.get_paginator.return_value = mock_paginator

    stockholm_obj = {
        "Key": "AWSLogs/195236889241/CloudTrail/eu-north-1/2026/10/20/log1.json.gz",
        "LastModified": "2026-10-20T09:10:00Z",
        "ETag": '"etag-eu-1"'
    }
    mumbai_obj = {
        "Key": "AWSLogs/195236889241/CloudTrail/ap-south-1/2026/10/20/log2.json.gz",
        "LastModified": "2026-10-20T08:00:00Z",
        "ETag": '"etag-ap-1"'
    }

    mock_paginator.paginate.return_value = [
        {"Contents": [stockholm_obj, mumbai_obj]}
    ]

    service = CloudTrailS3IngestionService(s3_client=mock_s3)
    objects = service._discover_objects("test-bucket", "AWSLogs/195236889241/CloudTrail/")

    assert len(objects) == 2
    # Mumbai obj modified earlier should be first after sort
    assert objects[0]["Key"] == mumbai_obj["Key"]
    assert objects[1]["Key"] == stockholm_obj["Key"]


# ==============================================================================
# 2. AWS Normalizer Stockholm ConsoleLogin Failure Tests
# ==============================================================================

def test_stockholm_console_login_failure_normalization():
    """Confirm AWS normalizer accurately classifies ConsoleLogin failure from Stockholm."""
    raw_event = {
        "eventVersion": "1.11",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAS25IGQKMUFW6CUV4C",
            "accountId": "195236889241",
            "userName": "test-analyst-corr"
        },
        "eventTime": "2026-10-20T09:02:44Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "eu-north-1",
        "sourceIPAddress": "49.43.135.72",
        "errorMessage": "Failed authentication",
        "responseElements": {"ConsoleLogin": "Failure"},
        "eventID": "e6e5f0ef-8d59-44fd-b789-b972d9cc2fe0",
        "readOnly": False,
        "provider": "AWS"
    }

    norm = aws_normalizer.normalize(raw_event)

    assert norm["provider"] == "AWS"
    assert norm["event_name"] == "ConsoleLogin"
    assert norm["event_type"] == "FAILED_LOGIN"
    assert norm["region"] == "eu-north-1"
    assert norm["source_ip"] == "49.43.135.72"
    assert norm["username"] == "test-analyst-corr"
    assert norm["event_time"] == "2026-10-20T09:02:44Z"
    assert norm["timestamp"] == "2026-10-20T09:02:44Z"
    assert norm["event_id"] == "e6e5f0ef-8d59-44fd-b789-b972d9cc2fe0"
    assert norm["event_category"] == "SECURITY"


def test_stockholm_console_login_failure_with_additional_event_data():
    """Verify fallback username extraction from additionalEventData for failed console sign-in."""
    raw_event = {
        "eventVersion": "1.11",
        "userIdentity": {},
        "additionalEventData": {
            "userName": "test-analyst-corr"
        },
        "eventTime": "2026-10-20T09:02:30Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "eu-north-1",
        "sourceIPAddress": "49.43.135.72",
        "errorMessage": "Failed authentication",
        "responseElements": {"ConsoleLogin": "Failure"},
        "eventID": "1b631dd2-180a-4dc7-a69c-08cf2affd892",
        "provider": "AWS"
    }

    norm = aws_normalizer.normalize(raw_event)

    assert norm["username"] == "test-analyst-corr"
    assert norm["event_type"] == "FAILED_LOGIN"
    assert norm["region"] == "eu-north-1"


# ==============================================================================
# 3. Authentication Correlation Rule Timestamp & Field Resilience
# ==============================================================================

def test_parse_event_timestamp_helper():
    """Verify _parse_event_timestamp handles datetime, ISO string, and None."""
    # Datetime with tz
    dt_utc = datetime(2026, 10, 20, 9, 2, 44, tzinfo=timezone.utc)
    assert _parse_event_timestamp({"timestamp": dt_utc}) == dt_utc

    # Datetime without tz
    dt_naive = datetime(2026, 10, 20, 9, 2, 44)
    res = _parse_event_timestamp({"timestamp": dt_naive})
    assert res.tzinfo == timezone.utc

    # ISO string with Z
    res_str = _parse_event_timestamp({"timestamp": "2026-10-20T09:02:44Z"})
    assert res_str == dt_utc

    # Fallback to event_time
    res_fallback = _parse_event_timestamp({"event_time": "2026-10-20T09:02:44Z"})
    assert res_fallback == dt_utc


def test_check_multiple_failed_logins_resilience_to_string_timestamps():
    """Verify correlation rule handles string timestamps and triggers at threshold 5."""
    recent_events = []
    for i in range(4):
        recent_events.append({
            "event_type": "FAILED_LOGIN",
            "username": "test-analyst-corr",
            "timestamp": f"2026-10-20T09:02:{30+i:02d}Z",
            "region": "eu-north-1",
            "source_ip": "49.43.135.72"
        })

    # 5th failed login
    current_event = {
        "event_type": "FAILED_LOGIN",
        "username": "test-analyst-corr",
        "provider": "AWS",
        "timestamp": "2026-10-20T09:02:34Z",
        "region": "eu-north-1",
        "source_ip": "49.43.135.72"
    }

    alerts = check_multiple_failed_logins(recent_events + [current_event], current_event)
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "MULTIPLE_FAILED_LOGINS"
    assert alerts[0]["username"] == "test-analyst-corr"
    assert alerts[0]["severity"] == "MEDIUM"


# ==============================================================================
# 4. Pipeline & Repository Top-Level Field Preservation Tests
# ==============================================================================

def test_pipeline_non_incident_event_preserves_top_level_region():
    """Verify single routine or single failed login retains top-level region, source_ip, timestamp."""
    raw_event = {
        "eventVersion": "1.11",
        "userIdentity": {"type": "IAMUser", "userName": "stockholm-operator"},
        "eventTime": "2026-10-20T09:05:16Z",
        "eventName": "DescribeRegions",
        "awsRegion": "eu-north-1",
        "sourceIPAddress": "49.43.135.72",
        "eventID": "test-desc-reg-001",
        "provider": "AWS"
    }

    result = incident_pipeline.process_event(raw_event)

    assert result["is_incident"] is False
    assert result["region"] == "eu-north-1"
    assert result["source_ip"] == "49.43.135.72"
    assert result["event_name"] == "DescribeRegions"
    assert "2026-10-20" in result["timestamp"]


def test_event_repository_save_event_enrichment():
    """Verify EventRepository defensively enriches missing top-level region, source_ip, timestamp."""
    mock_client = MagicMock()
    mock_client.indices.exists.return_value = True
    repo = EventRepository(opensearch_client=mock_client)

    # Incomplete event missing top-level region, source_ip, timestamp
    event_payload = {
        "event_id": "test-enrich-001",
        "event_summary": {
            "event_name": "ConsoleLogin",
            "region": "eu-north-1",
            "source_ip": "49.43.135.72",
            "timestamp": "2026-10-20T09:02:44Z"
        },
        "raw_log": {
            "awsRegion": "eu-north-1",
            "sourceIPAddress": "49.43.135.72",
            "eventTime": "2026-10-20T09:02:44Z"
        }
    }

    saved = repo.save_event(event_payload)

    assert saved["region"] == "eu-north-1"
    assert saved["source_ip"] == "49.43.135.72"
    assert saved["event_name"] == "ConsoleLogin"
    assert "2026-10-20" in saved["timestamp"]
    assert mock_client.index.called
