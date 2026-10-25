import json
from unittest.mock import MagicMock, patch, call
import pytest
from app.kafka.consumer import KafkaConsumerService


def test_kafka_commit_behavior_valid_message_commits_only_after_processing():
    """
    TC-KAFKA-005: Verify commit happens AFTER successful processing of a valid message.
    """
    service = KafkaConsumerService()

    valid_log = {
        "provider": "AWS",
        "eventName": "DescribeInstances",
        "sourceIPAddress": "192.168.1.100",
        "eventTime": "2026-10-08T07:45:00Z"
    }

    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.topic.return_value = "cloud_logs"
    mock_msg.partition.return_value = 0
    mock_msg.offset.return_value = 100
    mock_msg.value.return_value = json.dumps(valid_log).encode("utf-8")

    mock_consumer = MagicMock()
    mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt()]
    service.consumer = mock_consumer

    execution_order = []

    with patch("app.kafka.consumer.log_processor") as mock_log_processor:
        def fake_process(data):
            execution_order.append("process_log")
        mock_log_processor.process_log.side_effect = fake_process

        def fake_commit(msg):
            execution_order.append("commit")
        mock_consumer.commit.side_effect = fake_commit

        service.consume_logs()

        # Verify processing happens BEFORE commit
        assert execution_order == ["process_log", "commit"]
        mock_consumer.commit.assert_called_once_with(mock_msg)


def test_kafka_commit_behavior_failed_processing_does_not_commit():
    """
    TC-KAFKA-005: Verify that if log processing raises an exception, commit is NOT called.
    """
    service = KafkaConsumerService()

    valid_log = {"provider": "AWS", "eventName": "DescribeInstances"}
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.topic.return_value = "cloud_logs"
    mock_msg.partition.return_value = 0
    mock_msg.offset.return_value = 101
    mock_msg.value.return_value = json.dumps(valid_log).encode("utf-8")

    mock_consumer = MagicMock()
    mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt()]
    service.consumer = mock_consumer

    with patch("app.kafka.consumer.log_processor") as mock_log_processor:
        mock_log_processor.process_log.side_effect = RuntimeError("OpenSearch timeout")

        service.consume_logs()

        # Verify commit was NEVER called for the failed message
        mock_consumer.commit.assert_not_called()


def test_kafka_commit_behavior_malformed_json_commits_to_skip():
    """
    TC-KAFKA-005: Verify malformed JSON commits to skip unparseable message and avoid retry loops.
    """
    service = KafkaConsumerService()

    malformed_msg = MagicMock()
    malformed_msg.error.return_value = None
    malformed_msg.topic.return_value = "cloud_logs"
    malformed_msg.partition.return_value = 0
    malformed_msg.offset.return_value = 102
    malformed_msg.value.return_value = b'{"provider":"AWS","eventName":"TC-KAFKA-005"'

    mock_consumer = MagicMock()
    mock_consumer.poll.side_effect = [malformed_msg, KeyboardInterrupt()]
    service.consumer = mock_consumer

    with patch("app.kafka.consumer.log_processor") as mock_log_processor:
        service.consume_logs()

        # log_processor should not be called
        mock_log_processor.process_log.assert_not_called()
        # commit must be called to skip malformed message
        mock_consumer.commit.assert_called_once_with(malformed_msg)
