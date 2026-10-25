"""
Automated Test Suite: Multi-Region AWS CloudTrail S3 Ingestion
==============================================================

Covers all required verification scenarios:
 1. S3 object listing and pagination
 2. Filtering .json.gz objects
 3. Decompressing a valid gzip CloudTrail file
 4. Parsing a file containing multiple Records
 5. Preserving original CloudTrail fields
 6. Discovering logs from different Region folders
 7. Skipping already processed objects
 8. Restart-safe checkpoint behavior
 9. Duplicate eventID handling
10. Malformed JSON and invalid gzip handling
11. Empty Records arrays
12. Missing or malformed fields
13. Kafka publication failures and retries
14. Partial file-processing failure
15. Failed ConsoleLogin classification
16. Successful ConsoleLogin classification
17. Ensuring a failed file does not stop subsequent files
18. Ensuring the existing SQS ingestion pipeline remains unchanged
19. Scheduler startup and shutdown behavior
20. Regression tests for normalizers, correlation, risk scoring, incident generation
21. Configured named profile creates boto3 Session with profile and region
22. Empty or unset profile uses standard AWS credential provider chain
23. Credential precedence: named profile takes precedence over explicit keys
24. Dedicated explicit keys used when profile is unset
25. Boto3 session/client creation failure handled gracefully without crashing
"""

import gzip
import io
import json
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.config import get_settings
from app.correlation.correlation_engine import correlation_engine
from app.normalizer.aws import aws_normalizer
from app.pipeline.incident_pipeline import incident_pipeline
from app.alerts.alert_engine import alert_engine, AlertEngine
from app.services.aws_sqs_consumer import AWSSQSConsumer
from app.services.cloudtrail_s3_service import CloudTrailS3IngestionService
from app.services.log_processor import log_processor
from app.storage.incident_repository import incident_repository
from app.storage.s3_checkpoint_repository import S3CheckpointRepository, s3_checkpoint_repository

settings = get_settings()


# ==============================================================================
# Test Fixtures & Helpers
# ==============================================================================

def make_cloudtrail_gzip(records: list) -> bytes:
    """Helper to create valid in-memory gzip-compressed CloudTrail JSON."""
    payload = {"Records": records}
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json.dumps(payload).encode("utf-8"))
    return buf.getvalue()


def sample_failed_console_login_record() -> dict:
    """The verified real CloudTrail failed ConsoleLogin event."""
    return {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDA195236889241EXAMPLE",
            "arn": "arn:aws:iam::195236889241:user/security-analyst",
            "accountId": "195236889241",
            "userName": "security-analyst"
        },
        "eventTime": "2026-10-20T04:15:30Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "eu-north-1",
        "sourceIPAddress": "198.51.100.77",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "errorMessage": "Failed authentication",
        "requestParameters": None,
        "responseElements": {
            "ConsoleLogin": "Failure"
        },
        "additionalEventData": {
            "LoginTo": "https://console.aws.amazon.com/console/home",
            "MobileVersion": "No",
            "MFAUsed": "No"
        },
        "eventID": "c5f11a4e-9d22-4a0b-8d8a-361f3d82a101",
        "readOnly": False,
        "eventType": "AwsConsoleSignIn",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management"
    }


def sample_successful_console_login_record() -> dict:
    """A valid successful ConsoleLogin event."""
    return {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDA195236889241EXAMPLE",
            "arn": "arn:aws:iam::195236889241:user/security-analyst",
            "accountId": "195236889241",
            "userName": "security-analyst"
        },
        "eventTime": "2026-10-20T04:20:00Z",
        "eventSource": "signin.amazonaws.com",
        "eventName": "ConsoleLogin",
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "198.51.100.77",
        "errorMessage": None,
        "responseElements": {
            "ConsoleLogin": "Success"
        },
        "eventID": "d6f22b5f-0e33-5b1c-9e9b-472f4e93b202",
        "readOnly": False,
        "eventType": "AwsConsoleSignIn",
        "managementEvent": True,
        "recipientAccountId": "195236889241"
    }


@pytest.fixture
def isolated_checkpoint_repo():
    """Provides an isolated in-memory S3CheckpointRepository."""
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True
    repo = S3CheckpointRepository(opensearch_client=mock_os)
    repo.clear_local_cache()
    return repo


# ==============================================================================
# 1. S3 Object Listing and Pagination
# ==============================================================================

def test_01_s3_object_listing_and_pagination(isolated_checkpoint_repo):
    """Verify S3 pagination retrieves all objects across multiple pages in order."""
    mock_s3 = MagicMock()
    mock_paginator = MagicMock()

    # Simulate 2 pages of S3 results
    page1 = {
        "Contents": [
            {"Key": "AWSLogs/195236889241/CloudTrail/ap-south-1/2026/10/20/log1.json.gz", "LastModified": "2026-10-20T01:00:00Z"},
            {"Key": "AWSLogs/195236889241/CloudTrail/us-east-1/2026/10/20/log2.json.gz", "LastModified": "2026-10-20T02:00:00Z"},
        ]
    }
    page2 = {
        "Contents": [
            {"Key": "AWSLogs/195236889241/CloudTrail/eu-north-1/2026/10/20/log3.json.gz", "LastModified": "2026-10-20T03:00:00Z"},
        ]
    }
    mock_paginator.paginate.return_value = [page1, page2]
    mock_s3.get_paginator.return_value = mock_paginator

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)
    objects = service._discover_objects("my-bucket", "AWSLogs/195236889241/CloudTrail/")

    assert len(objects) == 3
    assert objects[0]["Key"].endswith("log1.json.gz")
    assert objects[1]["Key"].endswith("log2.json.gz")
    assert objects[2]["Key"].endswith("log3.json.gz")
    mock_s3.get_paginator.assert_called_once_with("list_objects_v2")


# ==============================================================================
# 2. Filtering .json.gz Objects
# ==============================================================================

def test_02_filtering_json_gz_objects(isolated_checkpoint_repo):
    """Verify non-.json.gz objects are ignored during discovery."""
    mock_s3 = MagicMock()
    mock_paginator = MagicMock()

    page = {
        "Contents": [
            {"Key": "AWSLogs/195236889241/CloudTrail/ap-south-1/valid.json.gz"},
            {"Key": "AWSLogs/195236889241/CloudTrail/ap-south-1/digest.json"},
            {"Key": "AWSLogs/195236889241/CloudTrail/ap-south-1/README.txt"},
            {"Key": "AWSLogs/195236889241/CloudTrail/eu-north-1/valid2.json.gz"},
        ]
    }
    mock_paginator.paginate.return_value = [page]
    mock_s3.get_paginator.return_value = mock_paginator

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)
    objects = service._discover_objects("my-bucket", "prefix/")

    assert len(objects) == 2
    assert all(obj["Key"].endswith(".json.gz") for obj in objects)


# ==============================================================================
# 3. Decompressing a Valid Gzip CloudTrail File
# ==============================================================================

def test_03_decompressing_valid_gzip_cloudtrail_file(isolated_checkpoint_repo):
    """Verify gzip content is correctly and safely decompressed."""
    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo)
    raw_json = json.dumps({"Records": [{"eventName": "TestEvent"}]}).encode("utf-8")

    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(raw_json)
    compressed_bytes = buf.getvalue()

    decompressed = service._decompress_gzip_safely(compressed_bytes)
    assert decompressed == raw_json


# ==============================================================================
# 4. Parsing a File Containing Multiple Records
# ==============================================================================

def test_04_parsing_file_containing_multiple_records(isolated_checkpoint_repo):
    """Verify that multiple records in a single file are extracted and published."""
    mock_s3 = MagicMock()
    records = [
        {"eventName": "Event1", "eventID": "id-1", "awsRegion": "ap-south-1"},
        {"eventName": "Event2", "eventID": "id-2", "awsRegion": "ap-south-1"},
        {"eventName": "Event3", "eventID": "id-3", "awsRegion": "ap-south-1"},
    ]
    gz_data = make_cloudtrail_gzip(records)
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        mock_kafka.producer.flush.return_value = 0

        result = service._process_file("my-bucket", "logs/test.json.gz", "etag-123")

        assert result["success"] is True
        assert result["records_published"] == 3
        assert mock_kafka.producer.produce.call_count == 3


# ==============================================================================
# 5. Preserving Original CloudTrail Fields
# ==============================================================================

def test_05_preserving_original_cloudtrail_fields(isolated_checkpoint_repo):
    """Verify all CloudTrail fields are preserved and ingestion metadata is attached."""
    mock_s3 = MagicMock()
    record = sample_failed_console_login_record()
    gz_data = make_cloudtrail_gzip([record])
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    published_messages = []
    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        def fake_produce(topic, value, callback):
            published_messages.append(json.loads(value))
        mock_kafka.producer.produce.side_effect = fake_produce
        mock_kafka.producer.flush.return_value = 0

        result = service._process_file("my-bucket", "logs/eu-north-1/test.json.gz", "etag-456")

        assert result["success"] is True
        assert len(published_messages) == 1
        msg = published_messages[0]

        # Verify all original fields are intact
        assert msg["eventID"] == record["eventID"]
        assert msg["eventName"] == "ConsoleLogin"
        assert msg["eventSource"] == "signin.amazonaws.com"
        assert msg["awsRegion"] == "eu-north-1"
        assert msg["sourceIPAddress"] == "198.51.100.77"
        assert msg["errorMessage"] == "Failed authentication"
        assert msg["responseElements"] == {"ConsoleLogin": "Failure"}
        assert msg["userIdentity"]["userName"] == "security-analyst"
        assert msg["managementEvent"] is True

        # Verify added ingestion metadata without field collision
        assert msg["provider"] == "AWS"
        assert msg["s3_bucket"] == "my-bucket"
        assert msg["s3_key"] == "logs/eu-north-1/test.json.gz"
        assert msg["s3_etag"] == "etag-456"
        assert msg["ingestion_source"] == "S3_CLOUDTRAIL"
        assert "ingestion_timestamp" in msg


# ==============================================================================
# 6. Discovering Logs from Different Region Folders
# ==============================================================================

def test_06_discovering_logs_from_different_region_folders(isolated_checkpoint_repo):
    """Verify discovery discovers logs from multiple regional subdirectories without per-region configs."""
    mock_s3 = MagicMock()
    mock_paginator = MagicMock()

    regional_files = [
        {"Key": "AWSLogs/195236889241/CloudTrail/eu-north-1/2026/10/20/log_eu.json.gz"},
        {"Key": "AWSLogs/195236889241/CloudTrail/us-east-1/2026/10/20/log_us.json.gz"},
        {"Key": "AWSLogs/195236889241/CloudTrail/ap-south-1/2026/10/20/log_ap.json.gz"},
    ]
    mock_paginator.paginate.return_value = [{"Contents": regional_files}]
    mock_s3.get_paginator.return_value = mock_paginator

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)
    objects = service._discover_objects("my-bucket", "AWSLogs/195236889241/CloudTrail/")

    assert len(objects) == 3
    regions_found = {obj["Key"].split("/")[3] for obj in objects}
    assert regions_found == {"eu-north-1", "us-east-1", "ap-south-1"}


# ==============================================================================
# 7. Skipping Already Processed Objects
# ==============================================================================

def test_07_skipping_already_processed_objects(isolated_checkpoint_repo):
    """Verify that an object already registered in the checkpoint repo is skipped."""
    isolated_checkpoint_repo.mark_file_processed(
        file_key="logs/already_done.json.gz",
        bucket="my-bucket",
        etag="etag-999",
        records_count=5
    )

    mock_s3 = MagicMock()
    mock_paginator = MagicMock()
    mock_paginator.paginate.return_value = [{
        "Contents": [
            {"Key": "logs/already_done.json.gz", "ETag": '"etag-999"'},
            {"Key": "logs/new_file.json.gz", "ETag": '"etag-new"'}
        ]
    }]
    mock_s3.get_paginator.return_value = mock_paginator

    new_file_gz = make_cloudtrail_gzip([{"eventName": "NewEvent", "eventID": "id-new"}])
    mock_s3.get_object.return_value = {"Body": io.BytesIO(new_file_gz)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        mock_kafka.producer.flush.return_value = 0
        stats = service.scan_and_process()

        assert stats["already_processed_files"] == 1
        assert stats["files_succeeded"] == 1
        assert stats["records_published"] == 1


# ==============================================================================
# 8. Restart-Safe Checkpoint Behavior
# ==============================================================================

def test_08_restart_safe_checkpoint_behavior(isolated_checkpoint_repo):
    """Verify that after service restart, previously processed files are remembered."""
    file_key = "logs/persisted.json.gz"
    isolated_checkpoint_repo.mark_file_processed(file_key, "my-bucket", "etag-111", records_count=2)

    # Instantiate brand new service instance simulating server restart
    new_service_instance = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo)
    assert isolated_checkpoint_repo.is_file_processed(file_key, "etag-111") is True


# ==============================================================================
# 9. Duplicate eventID Handling
# ==============================================================================

def test_09_duplicate_event_id_handling(isolated_checkpoint_repo):
    """Verify that an individual eventID already processed is skipped and not duplicated."""
    existing_event_id = "duplicate-uuid-999"
    isolated_checkpoint_repo.mark_event_processed(existing_event_id)

    mock_s3 = MagicMock()
    records = [
        {"eventName": "EventA", "eventID": existing_event_id, "awsRegion": "ap-south-1"},
        {"eventName": "EventB", "eventID": "unique-uuid-111", "awsRegion": "ap-south-1"},
    ]
    gz_data = make_cloudtrail_gzip(records)
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        mock_kafka.producer.flush.return_value = 0
        result = service._process_file("my-bucket", "logs/mixed.json.gz", "etag-mix")

        assert result["success"] is True
        assert result["records_published"] == 1
        assert result["duplicates_skipped"] == 1


# ==============================================================================
# 10. Malformed JSON and Invalid Gzip Handling
# ==============================================================================

def test_10_malformed_json_and_invalid_gzip_handling(isolated_checkpoint_repo):
    """Verify malformed gzip and broken JSON are logged and marked as failed without crashing."""
    mock_s3 = MagicMock()
    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    # 1. Corrupt Gzip
    mock_s3.get_object.return_value = {"Body": io.BytesIO(b"NOT_A_VALID_GZIP_STREAM")}
    res_gzip = service._process_file("my-bucket", "logs/corrupt.json.gz", "etag-bad-gz")
    assert res_gzip["success"] is False
    assert isolated_checkpoint_repo.get_retry_count("logs/corrupt.json.gz") == 1

    # 2. Corrupt JSON inside Gzip
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(b"NOT_VALID_JSON{:::broken")
    mock_s3.get_object.return_value = {"Body": io.BytesIO(buf.getvalue())}

    res_json = service._process_file("my-bucket", "logs/corrupt_json.json.gz", "etag-bad-json")
    assert res_json["success"] is False
    assert isolated_checkpoint_repo.get_retry_count("logs/corrupt_json.json.gz") == 1


# ==============================================================================
# 11. Empty Records Arrays
# ==============================================================================

def test_11_empty_records_arrays(isolated_checkpoint_repo):
    """Verify files with empty 'Records': [] (heartbeat logs) are marked as processed cleanly."""
    mock_s3 = MagicMock()
    empty_gz = make_cloudtrail_gzip([])
    mock_s3.get_object.return_value = {"Body": io.BytesIO(empty_gz)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)
    res = service._process_file("my-bucket", "logs/heartbeat.json.gz", "etag-empty")

    assert res["success"] is True
    assert res["records_published"] == 0
    assert isolated_checkpoint_repo.is_file_processed("logs/heartbeat.json.gz") is True


# ==============================================================================
# 12. Missing or Malformed Fields
# ==============================================================================

def test_12_missing_or_malformed_fields(isolated_checkpoint_repo):
    """Verify JSON without 'Records' array or non-list Records is handled gracefully."""
    mock_s3 = MagicMock()
    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    # Missing Records key completely
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(json.dumps({"someOtherKey": 123}).encode("utf-8"))
    mock_s3.get_object.return_value = {"Body": io.BytesIO(buf.getvalue())}

    res = service._process_file("my-bucket", "logs/no_records.json.gz", "etag-none")
    assert res["success"] is False
    assert isolated_checkpoint_repo.is_file_processed("logs/no_records.json.gz") is False


# ==============================================================================
# 13. Kafka Publication Failures and Retries
# ==============================================================================

def test_13_kafka_publication_failures_and_retries(isolated_checkpoint_repo):
    """Verify Kafka failure leaves file unconfirmed and increments retry count."""
    mock_s3 = MagicMock()
    gz_data = make_cloudtrail_gzip([{"eventName": "EventX", "eventID": "id-x"}])
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        # Simulate flush timeout remaining > 0
        mock_kafka.producer.flush.return_value = 1

        res = service._process_file("my-bucket", "logs/kafka_fail.json.gz", "etag-kf")

        assert res["success"] is False
        assert isolated_checkpoint_repo.is_file_processed("logs/kafka_fail.json.gz") is False
        assert isolated_checkpoint_repo.get_retry_count("logs/kafka_fail.json.gz") == 1


# ==============================================================================
# 14. Partial File-Processing Failure
# ==============================================================================

def test_14_partial_file_processing_failure(isolated_checkpoint_repo):
    """Verify partial failure does not mark file as processed."""
    mock_s3 = MagicMock()
    records = [
        {"eventName": "Event1", "eventID": "id-part-1"},
        {"eventName": "Event2", "eventID": "id-part-2"},
    ]
    gz_data = make_cloudtrail_gzip(records)
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_data)}

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        # Simulate exception during produce
        mock_kafka.producer.produce.side_effect = [None, RuntimeError("Kafka broker disconnected")]

        res = service._process_file("my-bucket", "logs/partial.json.gz", "etag-part")
        assert res["success"] is False
        assert isolated_checkpoint_repo.is_file_processed("logs/partial.json.gz") is False


# ==============================================================================
# 15. Failed ConsoleLogin Classification
# ==============================================================================

def test_15_failed_console_login_classification():
    """Verify that the verified failed ConsoleLogin event normalizes to FAILED_LOGIN."""
    raw_event = sample_failed_console_login_record()
    normalized = aws_normalizer.normalize(raw_event)

    assert normalized["provider"] == "AWS"
    assert normalized["event_type"] == "FAILED_LOGIN"
    assert normalized["event_name"] == "ConsoleLogin"
    assert normalized["username"] == "security-analyst"
    assert normalized["region"] == "eu-north-1"
    assert normalized["source_ip"] == "198.51.100.77"
    assert normalized["event_id"] == "c5f11a4e-9d22-4a0b-8d8a-361f3d82a101"
    assert normalized["raw_log"]["responseElements"]["ConsoleLogin"] == "Failure"


# ==============================================================================
# 16. Successful ConsoleLogin Classification
# ==============================================================================

def test_16_successful_console_login_classification():
    """Verify that a successful ConsoleLogin normalizes to AUTHENTICATION and not FAILED_LOGIN."""
    raw_event = sample_successful_console_login_record()
    normalized = aws_normalizer.normalize(raw_event)

    assert normalized["provider"] == "AWS"
    assert normalized["event_type"] == "AUTHENTICATION"
    assert normalized["event_name"] == "ConsoleLogin"
    assert normalized["username"] == "security-analyst"
    assert normalized["region"] == "ap-south-1"


# ==============================================================================
# 17. Ensuring a Failed File Does Not Stop Subsequent Files
# ==============================================================================

def test_17_failed_file_does_not_stop_subsequent_files(isolated_checkpoint_repo):
    """Verify that an error in file 1 does not abort the processing of file 2 and 3."""
    mock_s3 = MagicMock()
    mock_paginator = MagicMock()

    files = [
        {"Key": "logs/file1_corrupt.json.gz", "ETag": '"etag-1"'},
        {"Key": "logs/file2_valid.json.gz", "ETag": '"etag-2"'},
        {"Key": "logs/file3_valid.json.gz", "ETag": '"etag-3"'},
    ]
    mock_paginator.paginate.return_value = [{"Contents": files}]
    mock_s3.get_paginator.return_value = mock_paginator

    def fake_get_object(Bucket, Key):
        if "file1" in Key:
            return {"Body": io.BytesIO(b"CORRUPT")}
        valid_rec = [{"eventName": "OkEvent", "eventID": f"id-{Key}"}]
        return {"Body": io.BytesIO(make_cloudtrail_gzip(valid_rec))}

    mock_s3.get_object.side_effect = fake_get_object

    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo, s3_client=mock_s3)

    with patch("app.services.cloudtrail_s3_service.kafka_producer") as mock_kafka:
        mock_kafka.producer.flush.return_value = 0
        stats = service.scan_and_process()

        assert stats["files_attempted"] == 3
        assert stats["files_failed"] == 1
        assert stats["files_succeeded"] == 2
        assert stats["records_published"] == 2
        assert isolated_checkpoint_repo.is_file_processed("logs/file2_valid.json.gz") is True
        assert isolated_checkpoint_repo.is_file_processed("logs/file3_valid.json.gz") is True


# ==============================================================================
# 18. Ensuring the Existing SQS Ingestion Pipeline Remains Unchanged
# ==============================================================================

def test_18_existing_sqs_ingestion_pipeline_remains_unchanged():
    """Verify that AWSSQSConsumer continues to operate independently and correctly."""
    consumer = AWSSQSConsumer()

    sqs_message = {
        "MessageId": "sqs-msg-123",
        "ReceiptHandle": "receipt-xyz",
        "Body": json.dumps({
            "source": "aws.signin",
            "account": "195236889241",
            "region": "eu-north-1",
            "time": "2026-10-20T04:15:30Z",
            "detail": {
                "eventName": "ConsoleLogin",
                "eventSource": "signin.amazonaws.com",
                "awsRegion": "eu-north-1",
                "sourceIPAddress": "198.51.100.77",
                "userIdentity": {"userName": "analyst"},
                "responseElements": {"ConsoleLogin": "Failure"}
            }
        })
    }

    mock_sqs = MagicMock()
    consumer._sqs = mock_sqs

    published_sqs_events = []
    with patch("app.services.aws_sqs_consumer.kafka_producer") as mock_kafka:
        def fake_produce(topic, value, callback):
            published_sqs_events.append(json.loads(value))
        mock_kafka.producer.produce.side_effect = fake_produce
        mock_kafka.producer.flush.return_value = 0

        consumer._process_message(sqs_message)

        # SQS message deleted after Kafka delivery
        mock_sqs.delete_message.assert_called_once_with(
            QueueUrl=consumer._queue_url,
            ReceiptHandle="receipt-xyz"
        )
        assert len(published_sqs_events) == 1
        assert published_sqs_events[0]["provider"] == "AWS"
        assert published_sqs_events[0]["eventName"] == "ConsoleLogin"


# ==============================================================================
# 19. Scheduler Startup and Shutdown Behavior
# ==============================================================================

def test_19_scheduler_startup_and_shutdown_behavior(isolated_checkpoint_repo):
    """Verify thread lifecycle, disabled by default, and graceful shutdown."""
    service = CloudTrailS3IngestionService(checkpoint_repo=isolated_checkpoint_repo)

    # 1. Disabled by default
    with patch.object(settings, "CLOUDTRAIL_S3_INGESTION_ENABLED", False):
        service.start()
        assert service._thread is None

    # 2. Enabled starts background thread
    with patch.object(settings, "CLOUDTRAIL_S3_INGESTION_ENABLED", True), \
         patch.object(settings, "CLOUDTRAIL_S3_BUCKET", "test-bucket"), \
         patch.object(settings, "CLOUDTRAIL_S3_SCAN_INTERVAL_SECONDS", 300), \
         patch.object(service, "_create_s3_client", return_value=MagicMock()):

        service.start()
        assert service._thread is not None
        assert service._thread.is_alive()

        # Guard against double start
        existing_thread = service._thread
        service.start()
        assert service._thread is existing_thread

        # Clean shutdown
        service.stop()
        assert not service._thread.is_alive()


# ==============================================================================
# 20. Regression Tests for Normalizers, Correlation, Risk Scoring, Incident Generation
# ==============================================================================

def test_20_regression_normalizer_correlation_risk_pipeline():
    """
    Verify full end-to-end pipeline processing:
    Failed console logins from S3 format correctly trigger correlation rules
    and generate a high-risk security incident.
    """
    correlation_engine.event_store.clear()

    # Generate 5 consecutive failed logins to trigger MULTIPLE_FAILED_LOGINS rule (threshold=5)
    incident = None
    for i in range(5):
        raw_event = sample_failed_console_login_record()
        raw_event["eventID"] = f"event-seq-{i}"
        raw_event["eventTime"] = f"2026-10-20T04:1{i}:00Z"
        raw_event["provider"] = "AWS"

        with patch("app.pipeline.incident_pipeline.threat_service") as mock_threat:
            mock_threat.analyze_log.return_value = {
                "threat_score": 20,
                "threat_level": "LOW",
                "threat_tags": ["FAILED_LOGIN_SERIES"]
            }
            incident = incident_pipeline.process_event(raw_event)

    assert incident is not None
    assert incident["status"] == "OPEN"
    assert incident["username"] == "security-analyst"
    assert incident["provider"] == "AWS"
    # Alerts should include MULTIPLE_FAILED_LOGINS
    alert_types = [a["alert_type"] for a in incident.get("alerts", [])]
    assert "MULTIPLE_FAILED_LOGINS" in alert_types

    # Risk score must be calculated and > 0
    assert incident["risk_score"] > 0
    assert incident["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    correlation_engine.event_store.clear()


# ==============================================================================
# 21. Configured Profile Creates Boto3 Session with Profile and Region
# ==============================================================================

def test_21_configured_profile_creates_boto3_session_with_profile_and_region():
    """Verify configured CLOUDTRAIL_S3_AWS_PROFILE creates boto3 Session with profile and region."""
    service = CloudTrailS3IngestionService()

    with patch.object(settings, "CLOUDTRAIL_S3_AWS_PROFILE", "cloudguardian-s3"), \
         patch.object(settings, "CLOUDTRAIL_S3_REGION", "ap-south-1"), \
         patch("boto3.Session") as mock_session_cls:

        mock_session_instance = MagicMock()
        mock_session_cls.return_value = mock_session_instance
        mock_client = MagicMock()
        mock_session_instance.client.return_value = mock_client

        client = service._create_s3_client()

        mock_session_cls.assert_called_once_with(
            profile_name="cloudguardian-s3",
            region_name="ap-south-1"
        )
        mock_session_instance.client.assert_called_once_with("s3")
        assert client is mock_client


# ==============================================================================
# 22. Empty or Unset Profile Uses Standard AWS Credential Provider Chain
# ==============================================================================

def test_22_empty_or_unset_profile_uses_standard_credential_chain():
    """Verify empty/None CLOUDTRAIL_S3_AWS_PROFILE uses standard AWS credential provider chain."""
    service = CloudTrailS3IngestionService()

    with patch.object(settings, "CLOUDTRAIL_S3_AWS_PROFILE", None), \
         patch.object(settings, "CLOUDTRAIL_S3_ACCESS_KEY_ID", None), \
         patch.object(settings, "CLOUDTRAIL_S3_SECRET_ACCESS_KEY", None), \
         patch.object(settings, "AWS_ACCESS_KEY_ID", None), \
         patch.object(settings, "AWS_SECRET_ACCESS_KEY", None), \
         patch.object(settings, "CLOUDTRAIL_S3_REGION", "ap-south-1"), \
         patch("boto3.Session") as mock_session_cls:

        mock_session_instance = MagicMock()
        mock_session_cls.return_value = mock_session_instance
        mock_client = MagicMock()
        mock_session_instance.client.return_value = mock_client

        client = service._create_s3_client()

        # profile_name must not be passed, standard session with region
        mock_session_cls.assert_called_once_with(
            region_name="ap-south-1"
        )
        mock_session_instance.client.assert_called_once_with("s3")
        assert client is mock_client


# ==============================================================================
# 23. Credential Precedence: Named Profile over Explicit Access Keys
# ==============================================================================

def test_23_credential_precedence_profile_over_explicit_keys():
    """Verify named profile takes precedence over explicit IAM keys when both are configured."""
    service = CloudTrailS3IngestionService()

    with patch.object(settings, "CLOUDTRAIL_S3_AWS_PROFILE", "cloudguardian-s3"), \
         patch.object(settings, "CLOUDTRAIL_S3_ACCESS_KEY_ID", "EXPLICIT_KEY"), \
         patch.object(settings, "CLOUDTRAIL_S3_SECRET_ACCESS_KEY", "EXPLICIT_SECRET"), \
         patch.object(settings, "CLOUDTRAIL_S3_REGION", "ap-south-1"), \
         patch("boto3.Session") as mock_session_cls:

        mock_session_instance = MagicMock()
        mock_session_cls.return_value = mock_session_instance

        service._create_s3_client()

        # Must use profile_name, not aws_access_key_id
        mock_session_cls.assert_called_once_with(
            profile_name="cloudguardian-s3",
            region_name="ap-south-1"
        )


# ==============================================================================
# 24. Explicit Dedicated Keys Used When Profile Unset
# ==============================================================================

def test_24_dedicated_keys_used_when_profile_unset():
    """Verify explicit dedicated S3 keys are used when profile is unset."""
    service = CloudTrailS3IngestionService()

    with patch.object(settings, "CLOUDTRAIL_S3_AWS_PROFILE", None), \
         patch.object(settings, "CLOUDTRAIL_S3_ACCESS_KEY_ID", "DEDICATED_KEY"), \
         patch.object(settings, "CLOUDTRAIL_S3_SECRET_ACCESS_KEY", "DEDICATED_SECRET"), \
         patch.object(settings, "AWS_ACCESS_KEY_ID", "SHARED_KEY"), \
         patch.object(settings, "AWS_SECRET_ACCESS_KEY", "SHARED_SECRET"), \
         patch.object(settings, "CLOUDTRAIL_S3_REGION", "ap-south-1"), \
         patch("boto3.Session") as mock_session_cls:

        mock_session_instance = MagicMock()
        mock_session_cls.return_value = mock_session_instance

        service._create_s3_client()

        mock_session_cls.assert_called_once_with(
            region_name="ap-south-1",
            aws_access_key_id="DEDICATED_KEY",
            aws_secret_access_key="DEDICATED_SECRET"
        )


# ==============================================================================
# 25. Boto3 Session/Client Creation Failure Handled Gracefully
# ==============================================================================

def test_25_session_creation_failure_handled_gracefully():
    """Verify session/client creation errors (e.g. invalid profile) return None without crashing."""
    service = CloudTrailS3IngestionService()

    with patch.object(settings, "CLOUDTRAIL_S3_AWS_PROFILE", "non-existent-profile"), \
         patch("boto3.Session", side_effect=Exception("The config profile (non-existent-profile) could not be found")):

        client = service._create_s3_client()
        assert client is None


# ==============================================================================
# 26. Cross-Stream SQS and S3 eventID Deduplication
# ==============================================================================

def test_26_cross_stream_sqs_and_s3_event_id_deduplication():
    """Verify an event processed by SQS is not re-published by S3 ingestion."""
    repo = S3CheckpointRepository()
    repo.clear_local_cache()

    event_id = "evt-cross-stream-100"
    repo.mark_event_processed(event_id, file_key="SQS")
    assert repo.is_event_processed(event_id) is True

    rec = sample_failed_console_login_record()
    rec["eventID"] = event_id
    gz_bytes = make_cloudtrail_gzip([rec])

    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_bytes)}
    service = CloudTrailS3IngestionService(checkpoint_repo=repo, s3_client=mock_s3)

    with patch.object(service, "_publish_records_to_kafka") as mock_pub:
        res = service._process_file("test-bucket", "test-key.json.gz", "etag-100")
        assert res["success"] is True
        assert res["records_published"] == 0
        assert res["duplicates_skipped"] == 1
        mock_pub.assert_not_called()


# ==============================================================================
# 27. SQS Drops Duplicate eventID Already Ingested by S3
# ==============================================================================

def test_27_sqs_duplicate_event_id_dropped_before_kafka():
    """Verify SQS consumer drops duplicate CloudTrail event if already ingested via S3."""
    repo = S3CheckpointRepository()
    repo.clear_local_cache()

    event_id = "evt-s3-ingested-200"
    repo.mark_event_processed(event_id, file_key="s3://bucket/key.json.gz")

    consumer = AWSSQSConsumer()
    consumer._sqs = MagicMock()

    sqs_msg = {
        "ReceiptHandle": "rh-200",
        "MessageId": "msg-200",
        "Body": json.dumps({
            "source": "aws.signin",
            "detail": {
                "eventID": event_id,
                "eventName": "ConsoleLogin",
                "eventSource": "signin.amazonaws.com"
            }
        })
    }

    with patch("app.services.aws_sqs_consumer.s3_checkpoint_repository", repo), \
         patch("app.services.aws_sqs_consumer.kafka_producer") as mock_kafka:

        consumer._process_message(sqs_msg)

        consumer._sqs.delete_message.assert_called_once_with(
            QueueUrl=consumer._queue_url,
            ReceiptHandle="rh-200"
        )
        mock_kafka.producer.produce.assert_not_called()


# ==============================================================================
# 28. Deterministic Incident ID for Same Event ID
# ==============================================================================

def test_28_deterministic_incident_id_for_same_event_id():
    """Verify that multiple processing attempts of the same eventID yield identical incident_id."""
    engine = AlertEngine()
    event_id = "evt-deterministic-300"
    event_time = "2026-10-20T12:00:00Z"

    event = {
        "event_id": event_id,
        "event_time": event_time,
        "event_name": "ListManagedNotificationEvents",
        "region": "us-east-1",
        "source_ip": "198.51.100.77",
        "username": "analyst",
        "provider": "AWS"
    }
    risk_result = {"level": "LOW", "score": 0, "alerts": []}

    inc1 = engine.generate_incident(event, risk_result)
    inc2 = engine.generate_incident(event, risk_result)

    assert inc1["incident_id"] == inc2["incident_id"]
    assert inc1["incident_id"].startswith("INC-20261020-")


# ==============================================================================
# 29. Distinct Event IDs Produce Distinct Incident IDs (Legitimate Events Preserved)
# ==============================================================================

def test_29_distinct_event_ids_produce_distinct_incidents():
    """Verify that distinct events produce distinct incident IDs without suppressing legitimate events."""
    engine = AlertEngine()

    event_a = {
        "event_id": "evt-alpha-001",
        "event_time": "2026-10-20T12:00:00Z",
        "event_name": "ListManagedNotificationEvents",
        "provider": "AWS"
    }
    event_b = {
        "event_id": "evt-beta-002",
        "event_time": "2026-10-20T12:00:00Z",
        "event_name": "ListManagedNotificationEvents",
        "provider": "AWS"
    }
    risk_result = {"level": "LOW", "score": 0, "alerts": []}

    inc_a = engine.generate_incident(event_a, risk_result)
    inc_b = engine.generate_incident(event_b, risk_result)

    assert inc_a["incident_id"] != inc_b["incident_id"]


# ==============================================================================
# 30. LogProcessor Deduplicates and Suppresses Duplicate WebSocket Notifications
# ==============================================================================

def test_30_log_processor_deduplicates_and_suppresses_duplicate_websocket():
    """Verify LogProcessor detects an already-stored incident and skips duplicate persistence/broadcast."""
    incident_repository.clear_local_cache()

    raw_log = {
        "provider": "AWS",
        "eventID": "evt-log-proc-400",
        "eventTime": "2026-10-20T12:30:00Z",
        "eventName": "ListManagedNotificationEvents",
        "eventSource": "notifications.amazonaws.com",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.77",
        "userIdentity": {"userName": "analyst"}
    }

def test_30_log_processor_deduplicates_and_suppresses_duplicate_websocket():
    """Verify duplicate incident processing does not broadcast a duplicate WebSocket notification."""
    incident_repository.clear_local_cache()

    raw_log = {
        "provider": "AWS",
        "eventID": "evt-dup-test-400",
        "eventTime": "2026-10-20T12:30:00Z",
        "eventName": "ConsoleLogin",
        "errorMessage": "Failed authentication",
        "sourceIPAddress": "198.51.100.55",
        "userIdentity": {"userName": "admin"}
    }

    unique_inc_id = f"INC-20261020-t30-{uuid.uuid4().hex[:6]}"
    mock_incident = {
        "incident_id": unique_inc_id,
        "is_incident": True,
        "event_id": "evt-dup-test-400",
        "title": "ConsoleLogin Activity",
        "event_name": "ConsoleLogin",
        "status": "OPEN",
        "priority": "HIGH",
        "risk_score": 80,
        "risk_level": "HIGH",
        "username": "admin",
        "provider": "AWS",
        "created_at": "2026-10-20T12:30:00Z",
        "threat_score": 0,
        "threat_level": "NONE",
        "threat_tags": []
    }

    with patch("app.services.log_processor.ws_manager") as mock_ws, \
         patch.object(incident_repository.client, "get", side_effect=Exception("Not found")), \
         patch.object(incident_repository.client, "index"), \
         patch("app.services.log_processor.incident_pipeline.process_event", return_value=mock_incident):

        # First run: incident created and stored, broadcast sent
        inc1 = log_processor.process_log(raw_log)
        assert mock_ws.broadcast_sync.call_count == 1

        # Second run: duplicate event processed
        inc2 = log_processor.process_log(raw_log)
        # Should return the same incident
        assert inc2["incident_id"] == inc1["incident_id"]
        # WebSocket broadcast MUST NOT be called a second time
        assert mock_ws.broadcast_sync.call_count == 1


# ==============================================================================
# 31. Safe Incident Data Includes Title and Event Name
# ==============================================================================

def test_31_safe_incident_data_includes_title_and_event_name():
    """Verify WebSocket broadcast includes valid title and event_name instead of 'Unknown'."""
    incident_repository.clear_local_cache()

    raw_log = {
        "provider": "AWS",
        "eventID": "evt-title-500",
        "eventTime": "2026-10-20T12:45:00Z",
        "eventName": "ListManagedNotificationEvents",
        "eventSource": "notifications.amazonaws.com",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.77",
        "userIdentity": {"userName": "analyst"}
    }

    unique_inc_id = f"INC-20261020-t31-{uuid.uuid4().hex[:6]}"
    mock_incident = {
        "incident_id": unique_inc_id,
        "is_incident": True,
        "event_id": "evt-title-500",
        "title": "ListManagedNotificationEvents Activity",
        "event_name": "ListManagedNotificationEvents",
        "status": "OPEN",
        "priority": "MEDIUM",
        "risk_score": 50,
        "risk_level": "MEDIUM",
        "username": "analyst",
        "provider": "AWS",
        "created_at": "2026-10-20T12:45:00Z",
        "threat_score": 0,
        "threat_level": "NONE",
        "threat_tags": []
    }

    with patch("app.services.log_processor.ws_manager") as mock_ws, \
         patch.object(incident_repository.client, "get", side_effect=Exception("Not found")), \
         patch.object(incident_repository.client, "index"), \
         patch("app.services.log_processor.incident_pipeline.process_event", return_value=mock_incident):

        log_processor.process_log(raw_log)

        assert mock_ws.broadcast_sync.called
        call_payload = mock_ws.broadcast_sync.call_args[0][0]
        data = call_payload["data"]
        assert data["event_name"] == "ListManagedNotificationEvents"
        assert "ListManagedNotificationEvents" in data["title"]
        assert data["event_name"] != "Unknown"


# ==============================================================================
# 32. Repeated S3 Scan Skips Already Processed Files
# ==============================================================================

def test_32_repeated_s3_scan_skips_already_processed_files():
    """Verify a second scan cycle over the same bucket/files skips already processed objects."""
    mock_os = MagicMock()
    mock_os.get.side_effect = Exception("Not found")
    mock_os.indices.exists.return_value = True
    repo = S3CheckpointRepository(opensearch_client=mock_os)
    repo.clear_local_cache()

    rec = sample_failed_console_login_record()
    rec["eventID"] = "c5f11a4e-repeat-test-unique-32"
    gz_bytes = make_cloudtrail_gzip([rec])

    mock_s3 = MagicMock()
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "AWSLogs/195236889241/CloudTrail/us-east-1/log1-unique32.json.gz", "ETag": '"etag-repeat"'}]}
    ]
    mock_s3.get_object.return_value = {"Body": io.BytesIO(gz_bytes)}

    service = CloudTrailS3IngestionService(checkpoint_repo=repo, s3_client=mock_s3)

    with patch.object(service, "_publish_records_to_kafka", return_value={"success": True}):
        # Cycle 1: file is processed
        stats1 = service.scan_and_process()
        assert stats1["files_succeeded"] == 1
        assert stats1["already_processed_files"] == 0

        # Cycle 2: same file discovered again
        stats2 = service.scan_and_process()
        assert stats2["files_succeeded"] == 0
        assert stats2["already_processed_files"] == 1
        assert stats2["files_succeeded"] == 0
        assert stats2["already_processed_files"] == 1


# ==============================================================================
# 33. Restart-Safe Checkpoint Restores from OpenSearch
# ==============================================================================

def test_33_restart_safe_checkpoint_restores_from_opensearch():
    """Verify checkpoint repository reconstructs state from OpenSearch upon application restart."""
    mock_os = MagicMock()
    mock_os.get.return_value = {
        "_source": {
            "status": "PROCESSED",
            "etag": "etag-restart-123",
            "file_key": "some-key.json.gz"
        }
    }
    mock_os.indices.exists.return_value = True

    restarted_repo = S3CheckpointRepository(opensearch_client=mock_os)
    assert restarted_repo.is_file_processed("some-key.json.gz", "etag-restart-123") is True


# ==============================================================================
# 34. Failed Kafka Publication Leaves File Unconfirmed and Retried
# ==============================================================================

def test_34_failed_kafka_publication_not_marked_processed_and_retried():
    """Verify Kafka delivery failure leaves file unconfirmed and retries on subsequent scan."""
    mock_os = MagicMock()
    mock_os.get.return_value = {"found": False}
    repo = S3CheckpointRepository(opensearch_client=mock_os)
    repo.clear_local_cache()

    rec = sample_failed_console_login_record()
    rec["eventID"] = "c5f11a4e-retry-unique-test-999"
    gz_bytes = make_cloudtrail_gzip([rec])

    mock_s3 = MagicMock()
    mock_s3.get_paginator.return_value.paginate.return_value = [
        {"Contents": [{"Key": "AWSLogs/195236889241/CloudTrail/us-east-1/retry-log.json.gz", "ETag": '"etag-retry"'}]}
    ]
    mock_s3.get_object.side_effect = lambda **kwargs: {"Body": io.BytesIO(gz_bytes)}

    service = CloudTrailS3IngestionService(checkpoint_repo=repo, s3_client=mock_s3)

    # First attempt: Kafka fails
    with patch.object(service, "_publish_records_to_kafka", return_value={"success": False, "error": "Broker down"}):
        stats1 = service.scan_and_process()
        assert stats1["files_failed"] == 1
        assert repo.is_file_processed("AWSLogs/195236889241/CloudTrail/us-east-1/retry-log.json.gz") is False
        assert repo.get_retry_count("AWSLogs/195236889241/CloudTrail/us-east-1/retry-log.json.gz") == 1

    # Second attempt: Kafka recovers
    with patch.object(service, "_publish_records_to_kafka", return_value={"success": True}):
        stats2 = service.scan_and_process()
        assert stats2["files_succeeded"] == 1
        assert repo.is_file_processed("AWSLogs/195236889241/CloudTrail/us-east-1/retry-log.json.gz") is True


# ==============================================================================
# 35. AWS User Notifications ListManagedNotificationEvents Normalized as MONITORING with Risk 0
# ==============================================================================

def test_35_aws_user_notifications_normalized_as_monitoring_with_risk_0():
    """Verify ListManagedNotificationEvents is categorized as MONITORING and receives risk score 0."""
    raw_event = {
        "eventVersion": "1.08",
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDA195236889241EXAMPLE",
            "arn": "arn:aws:iam::195236889241:user/security-analyst",
            "accountId": "195236889241",
            "userName": "security-analyst"
        },
        "eventTime": "2026-10-20T04:15:30Z",
        "eventSource": "notifications.amazonaws.com",
        "eventName": "ListManagedNotificationEvents",
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.77",
        "userAgent": "Mozilla/5.0",
        "eventID": "c5f11a4e-9d22-4a0b-8d8a-361f3d82a999",
        "readOnly": True,
        "eventType": "AwsApiCall",
        "managementEvent": True,
        "recipientAccountId": "195236889241",
        "eventCategory": "Management",
        "provider": "AWS"
    }

    normalized = aws_normalizer.normalize(raw_event)
    assert normalized["event_type"] == "MONITORING"
    assert normalized["event_name"] == "ListManagedNotificationEvents"
    assert normalized["region"] == "us-east-1"

    # Process through pipeline
    incident = incident_pipeline.process_event(raw_event)
    assert incident["risk_score"] == 0
    assert incident["risk_level"] == "LOW"
    assert incident["priority"] == "LOW"
    assert incident["analyst_attention"] == "NOT REQUIRED"

