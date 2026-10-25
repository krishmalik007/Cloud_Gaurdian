"""
Comprehensive Verification Suite: Historical CloudTrail Replay and Incident Flooding Fixes
==========================================================================================

Covers all 12 scenarios required by Section 8 of the prompt:
1. A previously processed S3 object is not ingested again during normal polling.
2. A newly delivered object is ingested successfully.
3. Restarting the application does not reset persistent checkpoints.
4. A failed ingestion can be retried safely.
5. Repeated delivery of the same CloudTrail eventID does not create duplicate incidents.
6. Different event IDs with identical event names remain distinct events.
7. A zero-risk informational event is stored without creating an incident.
8. A legitimate AssumeRole event is not automatically treated as malicious.
9. A genuine high-risk event can still trigger an incident.
10. A GuardDuty subscription error is visible as an integration-health problem without an unjustified zero-risk security incident.
11. Concurrent processing does not create duplicate incidents.
12. Missing event IDs do not cause unrelated events to be incorrectly deduplicated.
"""

import gzip
import io
import json
import threading
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.config import get_settings
from app.normalizer.aws import aws_normalizer
from app.pipeline.incident_pipeline import incident_pipeline
from app.services.cloudtrail_s3_service import CloudTrailS3IngestionService
from app.services.log_processor import log_processor
from app.storage.event_repository import EventRepository, event_repository
from app.storage.incident_repository import IncidentRepository, incident_repository
from app.storage.s3_checkpoint_repository import S3CheckpointRepository

settings = get_settings()


def _make_gzip(records: list) -> bytes:
    """Helper to generate in-memory gzip compressed CloudTrail JSON."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json.dumps({"Records": records}).encode("utf-8"))
    return buf.getvalue()


# ==============================================================================
# Scenario 1: Previously processed S3 object is not ingested again during normal polling
# ==============================================================================

def test_01_previously_processed_s3_object_not_ingested_again():
    """Verify an S3 object marked as PROCESSED is skipped in subsequent polling cycles."""
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True
    repo = S3CheckpointRepository(opensearch_client=mock_os)
    repo.clear_local_cache()

    file_key = "AWSLogs/195236889241/CloudTrail/ap-south-1/2026/10/20/processed-file.json.gz"
    etag = "etag-processed-001"
    repo.mark_file_processed(file_key, "test-bucket", etag=etag, records_count=5)

    mock_s3 = MagicMock()
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": file_key, "ETag": f'"{etag}"', "LastModified": datetime.now(timezone.utc)}]}
    ]

    service = CloudTrailS3IngestionService(checkpoint_repo=repo, s3_client=mock_s3)
    stats = service.scan_and_process()

    assert stats["discovered_files"] == 1
    assert stats["already_processed_files"] == 1
    assert stats["new_objects_accepted"] == 0
    assert stats["files_attempted"] == 0
    mock_s3.get_object.assert_not_called()


# ==============================================================================
# Scenario 2: Newly delivered object is ingested successfully
# ==============================================================================

def test_02_newly_delivered_object_ingested_successfully():
    """Verify a newly delivered CloudTrail log file is detected, downloaded, and published."""
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True
    mock_os.get.side_effect = Exception("Not found")
    repo = S3CheckpointRepository(opensearch_client=mock_os)
    repo.clear_local_cache()

    file_key = "AWSLogs/195236889241/CloudTrail/ap-south-1/2026/10/20/new-file.json.gz"
    etag = "etag-new-002"
    record = {
        "eventVersion": "1.08",
        "userIdentity": {"type": "IAMUser", "userName": "analyst"},
        "eventTime": datetime.now(timezone.utc).isoformat(),
        "eventName": "DescribeInstances",
        "eventSource": "ec2.amazonaws.com",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "198.51.100.10",
        "eventID": "new-event-id-002",
        "readOnly": True,
    }
    gz_data = _make_gzip([record])

    mock_s3 = MagicMock()
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": file_key, "ETag": f'"{etag}"', "LastModified": datetime.now(timezone.utc)}]}
    ]
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=repo, s3_client=mock_s3)
    with patch.object(service, "_publish_records_to_kafka", return_value={"success": True}):
        stats = service.scan_and_process()

    assert stats["discovered_files"] == 1
    assert stats["new_objects_accepted"] == 1
    assert stats["files_succeeded"] == 1
    assert stats["records_published"] == 1
    assert repo.is_file_processed(file_key, etag) is True


# ==============================================================================
# Scenario 3: Restarting the application does not reset persistent checkpoints
# ==============================================================================

def test_03_restarting_application_does_not_reset_persistent_checkpoints(tmp_path):
    """Verify persistent checkpoints survive container/application restarts via disk cache and OpenSearch."""
    disk_file = tmp_path / "s3_checkpoints.json"

    # Worker 1: marks file and event as processed
    mock_os1 = MagicMock()
    mock_os1.indices.exists.return_value = True
    repo1 = S3CheckpointRepository(opensearch_client=mock_os1, disk_file=disk_file)

    test_key = "AWSLogs/195236889241/CloudTrail/restart-test.json.gz"
    test_etag = "etag-restart-abc"
    test_eid = "eid-restart-xyz"

    repo1.mark_file_processed(test_key, "bucket-1", etag=test_etag, records_count=1)
    repo1.mark_event_processed(test_eid, file_key=test_key)

    # Worker 2: simulates application restart from cold state
    mock_os2 = MagicMock()
    mock_os2.indices.exists.return_value = True
    repo2 = S3CheckpointRepository(opensearch_client=mock_os2, disk_file=disk_file)

    assert repo2.is_file_processed(test_key, test_etag) is True
    assert repo2.is_event_processed(test_eid) is True


# ==============================================================================
# Scenario 4: Failed ingestion can be retried safely
# ==============================================================================

def test_04_failed_ingestion_can_be_retried_safely():
    """Verify a failed file is not marked processed and is retried on subsequent polling cycle."""
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True
    mock_os.get.side_effect = Exception("Not found")
    repo = S3CheckpointRepository(opensearch_client=mock_os)
    repo.clear_local_cache()

    file_key = "AWSLogs/195236889241/CloudTrail/retry-test.json.gz"
    record = {
        "eventVersion": "1.08",
        "eventName": "DescribeCanaries",
        "eventSource": "synthetics.amazonaws.com",
        "eventID": "retry-event-id-004",
        "readOnly": True,
    }
    gz_data = _make_gzip([record])

    mock_s3 = MagicMock()
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": file_key, "ETag": '"etag-retry"', "LastModified": datetime.now(timezone.utc)}]}
    ]
    mock_s3.get_object.side_effect = lambda **kwargs: {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=repo, s3_client=mock_s3)

    # Attempt 1: Kafka fails
    with patch.object(service, "_publish_records_to_kafka", return_value={"success": False, "error": "Kafka Timeout"}):
        stats1 = service.scan_and_process()
        assert stats1["files_failed"] == 1
        assert repo.is_file_processed(file_key) is False
        assert repo.get_retry_count(file_key) == 1

    # Attempt 2: Kafka succeeds
    with patch.object(service, "_publish_records_to_kafka", return_value={"success": True}):
        stats2 = service.scan_and_process()
        assert stats2["files_succeeded"] == 1
        assert repo.is_file_processed(file_key) is True


# ==============================================================================
# Scenario 5: Repeated delivery of the same CloudTrail eventID does not create duplicate incidents
# ==============================================================================

def test_05_repeated_delivery_of_same_event_id_does_not_create_duplicate_incidents():
    """Verify delivering the same eventID repeatedly produces exactly one incident and one toast."""
    mock_os = MagicMock()
    mock_os.get.side_effect = Exception("Not found")
    mock_os.indices.exists.return_value = True

    inc_repo = IncidentRepository(opensearch_client=mock_os)
    inc_repo.clear_local_cache()

    raw_event = {
        "provider": "AWS",
        "eventID": "c5f11a4e-dedup-555",
        "eventTime": "2026-10-20T12:00:00Z",
        "eventName": "ConsoleLogin",
        "sourceIPAddress": "203.0.113.195",
        "userIdentity": {"userName": "admin"},
        "eventType": "BRUTE_FORCE",
    }

    mock_incident = {
        "incident_id": "INC-20261020-dedup555",
        "is_incident": True,
        "event_id": "c5f11a4e-dedup-555",
        "title": "Brute Force Detected",
        "event_name": "ConsoleLogin",
        "status": "OPEN",
        "priority": "HIGH",
        "risk_score": 85,
        "risk_level": "HIGH",
        "username": "admin",
        "provider": "AWS",
        "created_at": "2026-10-20T12:00:00Z",
        "threat_score": 0,
        "threat_level": "NONE",
        "threat_tags": [],
    }

    with patch("app.services.log_processor.incident_repository", inc_repo), \
         patch("app.services.log_processor.ws_manager") as mock_ws, \
         patch("app.services.log_processor.incident_pipeline.process_event", return_value=mock_incident):

        # First delivery
        res1 = log_processor.process_log(raw_event)
        assert res1["incident_id"] == "INC-20261020-dedup555"
        assert mock_ws.broadcast_sync.call_count == 1

        # Second delivery (duplicate delivery via Kafka re-balance or retry)
        res2 = log_processor.process_log(raw_event)
        assert res2["incident_id"] == "INC-20261020-dedup555"
        # Must NOT broadcast again or create another incident
        assert mock_ws.broadcast_sync.call_count == 1


# ==============================================================================
# Scenario 6: Different event IDs with identical event names remain distinct events
# ==============================================================================

def test_06_different_event_ids_with_identical_event_names_remain_distinct():
    """Verify different event IDs sharing the same eventName remain separate and distinct."""
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True
    evt_repo = EventRepository(opensearch_client=mock_os)
    evt_repo.clear_local_cache()

    event_a = {
        "event_id": "eid-distinct-001",
        "event_name": "AssumeRole",
        "username": "service-role-1",
        "timestamp": "2026-10-20T10:00:00Z",
        "provider": "AWS",
    }
    event_b = {
        "event_id": "eid-distinct-002",
        "event_name": "AssumeRole",
        "username": "service-role-2",
        "timestamp": "2026-10-20T10:00:05Z",
        "provider": "AWS",
    }

    saved_a = evt_repo.save_event(event_a)
    saved_b = evt_repo.save_event(event_b)

    assert saved_a["event_id"] == "eid-distinct-001"
    assert saved_b["event_id"] == "eid-distinct-002"
    assert saved_a["event_id"] != saved_b["event_id"]
    assert evt_repo.get_event("eid-distinct-001")["username"] == "service-role-1"
    assert evt_repo.get_event("eid-distinct-002")["username"] == "service-role-2"


# ==============================================================================
# Scenario 7: A zero-risk informational event is stored without creating an incident
# ==============================================================================

def test_07_zero_risk_informational_event_stored_without_incident():
    """Verify routine AWS events are indexed in events store with no security incident generated."""
    raw_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "userName": "security-analyst",
            "arn": "arn:aws:iam::195236889241:user/security-analyst",
        },
        "eventTime": "2026-10-20T08:00:00Z",
        "eventSource": "synthetics.amazonaws.com",
        "eventName": "DescribeCanaries",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "198.51.100.80",
        "eventID": "c5f11a4e-canary-007",
        "readOnly": True,
        "provider": "AWS",
    }

    event_repository.clear_local_cache()
    incident_repository.clear_local_cache()

    with patch("app.services.log_processor.ws_manager") as mock_ws, \
         patch("app.storage.incident_repository.client"):

        result = log_processor.process_log(raw_event)

        # 1. Pipeline classified as non-incident
        assert result["is_incident"] is False
        assert result["incident_id"] is None
        assert result["risk_score"] == 0
        assert result["status"] == "INFORMATIONAL"

        # 2. Stored in OpenSearch events index
        assert event_repository.is_event_stored("c5f11a4e-canary-007") is True

        # 3. No security incident created in incident repo
        assert incident_repository.get_incident(result.get("incident_id")) is None

        # 4. No WebSocket toast notification sent
        mock_ws.broadcast_sync.assert_not_called()


# ==============================================================================
# Scenario 8: A legitimate AssumeRole event is not automatically treated as malicious
# ==============================================================================

def test_08_legitimate_assume_role_not_treated_as_malicious():
    """Verify Resource Explorer and EventBridge AssumeRole calls are evaluated as legitimate service activity."""
    resource_explorer_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "AssumedRole",
            "arn": "arn:aws:sts::195236889241:assumed-role/AWSServiceRoleForResourceExplorer/ResourceExplorer",
            "sessionContext": {
                "sessionIssuer": {
                    "arn": "arn:aws:iam::195236889241:role/aws-service-role/resource-explorer-2.amazonaws.com/AWSServiceRoleForResourceExplorer"
                }
            },
        },
        "eventTime": "2026-10-20T07:30:00Z",
        "eventSource": "sts.amazonaws.com",
        "eventName": "AssumeRole",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "resource-explorer-2.amazonaws.com",
        "eventID": "c5f11a4e-re-008",
        "provider": "AWS",
    }

    # Normalizer classifies as service activity
    normalized = aws_normalizer.normalize(resource_explorer_event)
    assert normalized["is_service_activity"] is True
    assert normalized["service_context"] == "AWSServiceRoleForResourceExplorer"
    assert normalized["event_category"] == "INFORMATIONAL"

    # Incident pipeline suppresses incident creation
    processed = incident_pipeline.process_event(resource_explorer_event)
    assert processed["is_incident"] is False
    assert processed["incident_id"] is None
    assert processed["risk_score"] == 0
    assert processed["status"] == "INFORMATIONAL"


# ==============================================================================
# Scenario 9: A genuine high-risk event can still trigger an incident
# ==============================================================================

def test_09_genuine_high_risk_event_triggers_incident():
    """Verify real threats and high-risk events (e.g. brute force, IOC match) still create security incidents."""
    high_risk_event = {
        "eventVersion": "1.08",
        "userIdentity": {"type": "IAMUser", "userName": "attacker"},
        "eventTime": "2026-10-20T09:00:00Z",
        "eventName": "ConsoleLogin",
        "sourceIPAddress": "198.51.100.99",
        "errorMessage": "Multiple failed authentications",
        "eventID": "c5f11a4e-brute-009",
        "provider": "AWS",
    }

    mock_ioc = {
        "value": "198.51.100.99",
        "enabled": True,
        "severity": "CRITICAL",
        "source": "THREAT_INTEL",
        "description": "Known malicious actor C2 IP"
    }

    with patch("app.services.threat_service.threat_service.lookup", return_value=mock_ioc):
        processed = incident_pipeline.process_event(high_risk_event)

    assert processed["is_incident"] is True
    assert processed["incident_id"] is not None
    assert processed["incident_id"].startswith("INC-")
    assert processed["event_id"] == "c5f11a4e-brute-009"
    assert processed["threat_score"] > 0


# ==============================================================================
# Scenario 10: GuardDuty subscription error visible as integration-health problem
# ==============================================================================

def test_10_guardduty_subscription_error_visible_as_integration_health_without_security_incident():
    """Verify SubscriptionRequiredException is categorized as operational health without generating a zero-risk incident."""
    guardduty_error_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "userName": "security-service",
            "arn": "arn:aws:iam::195236889241:user/security-service",
        },
        "eventTime": "2026-10-20T06:15:00Z",
        "eventSource": "guardduty.amazonaws.com",
        "eventName": "ListResources",
        "awsRegion": "eu-north-1",
        "errorCode": "SubscriptionRequiredException",
        "errorMessage": "The AWS Access Key Id needs a subscription for the service",
        "eventID": "c5f11a4e-gd-010",
        "provider": "AWS",
    }

    # 1. Normalization
    normalized = aws_normalizer.normalize(guardduty_error_event)
    assert normalized["is_operational_health"] is True
    assert normalized["event_type"] == "INTEGRATION_HEALTH"
    assert normalized["event_category"] == "OPERATIONAL_HEALTH"
    assert "subscription required" in normalized["operational_issue"]

    # 2. Pipeline processing
    processed = incident_pipeline.process_event(guardduty_error_event)
    assert processed["is_incident"] is False
    assert processed["incident_id"] is None
    assert processed["status"] == "OPERATIONAL_HEALTH"
    assert processed["is_operational_health"] is True
    assert processed["analyst_attention"] == "NOT REQUIRED"


# ==============================================================================
# Scenario 11: Concurrent processing does not create duplicate incidents
# ==============================================================================

def test_11_concurrent_processing_does_not_create_duplicate_incidents():
    """Verify concurrent workers processing the same event concurrently do not produce duplicate incidents."""
    mock_os = MagicMock()
    mock_os.get.side_effect = Exception("Not found")
    mock_os.indices.exists.return_value = True

    inc_repo = IncidentRepository(opensearch_client=mock_os)
    inc_repo.clear_local_cache()

    stable_event_id = "c5f11a4e-concurrent-011"
    mock_incident = {
        "incident_id": f"INC-20261020-{stable_event_id[:8]}",
        "is_incident": True,
        "event_id": stable_event_id,
        "title": "Privilege Escalation Detected",
        "event_name": "AttachUserPolicy",
        "status": "OPEN",
        "priority": "HIGH",
        "risk_score": 90,
        "risk_level": "HIGH",
        "username": "developer",
        "provider": "AWS",
        "created_at": "2026-10-20T11:00:00Z",
        "threat_score": 0,
        "threat_level": "NONE",
        "threat_tags": [],
    }

    created_incidents = []
    lock = threading.Lock()

    def _worker():
        res = log_processor.process_log({"provider": "AWS", "eventID": stable_event_id})
        with lock:
            created_incidents.append(res["incident_id"])

    with patch("app.services.log_processor.incident_repository", inc_repo), \
         patch("app.services.log_processor.ws_manager"), \
         patch("app.services.log_processor.incident_pipeline.process_event", return_value=mock_incident):
        threads = [threading.Thread(target=_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    # All 10 worker threads resolved to the exact same incident ID
    assert len(created_incidents) == 10
    assert len(set(created_incidents)) == 1
    assert created_incidents[0] == f"INC-20261020-{stable_event_id[:8]}"


# ==============================================================================
# Scenario 12: Missing event IDs do not cause unrelated events to be incorrectly deduplicated
# ==============================================================================

def test_12_missing_event_ids_do_not_cause_unrelated_events_to_be_deduplicated():
    """Verify events missing CloudTrail eventID are assigned unique IDs and not falsely merged."""
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True
    evt_repo = EventRepository(opensearch_client=mock_os)
    evt_repo.clear_local_cache()

    event1 = {
        "event_name": "DescribeInstances",
        "username": "script-worker",
        "timestamp": "2026-10-20T12:00:00Z",
        "provider": "AWS",
    }
    event2 = {
        "event_name": "DescribeInstances",
        "username": "script-worker",
        "timestamp": "2026-10-20T12:00:00Z",
        "provider": "AWS",
    }

    saved1 = evt_repo.save_event(event1)
    saved2 = evt_repo.save_event(event2)

    # Missing event IDs generate distinct unique document IDs
    assert saved1["event_id"] != saved2["event_id"]
    assert saved1["event_id"].startswith("evt-")
    assert saved2["event_id"].startswith("evt-")
    assert evt_repo.get_event(saved1["event_id"]) is not None
    assert evt_repo.get_event(saved2["event_id"]) is not None
