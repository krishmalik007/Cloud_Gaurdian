import json
from unittest.mock import MagicMock, patch
import pytest
from app.kafka.consumer import KafkaConsumerService


def test_kafka_consumer_handles_malformed_json_safely():
    """
    TC-KAFKA-003: Verify that malformed JSON in a Kafka message is handled safely,
    logged with an error, committed to prevent infinite retry loops, and does not crash the consumer.
    """
    service = KafkaConsumerService()

    # Create mock malformed Kafka message
    malformed_msg = MagicMock()
    malformed_msg.error.return_value = None
    malformed_msg.value.return_value = b'{"provider":"AWS","eventName":"TC-KAFKA-003"'

    # Create mock valid Kafka message for subsequent processing
    valid_log_dict = {
        "provider": "AWS",
        "eventName": "DescribeInstances",
        "sourceIPAddress": "192.168.1.100",
        "eventTime": "2026-10-08T07:20:00Z",
        "region": "ap-south-1"
    }
    valid_msg = MagicMock()
    valid_msg.error.return_value = None
    valid_msg.value.return_value = json.dumps(valid_log_dict).encode("utf-8")

    # Mock consumer instance
    mock_consumer = MagicMock()
    mock_consumer.poll.side_effect = [malformed_msg, valid_msg, None]
    service.consumer = mock_consumer

    # Track log processor calls
    with patch("app.kafka.consumer.log_processor") as mock_log_processor, \
         patch("app.kafka.consumer.logger") as mock_logger:

        # Run consume_logs loop for 2 messages
        # Stop event will trigger after processing the 2 messages
        def stop_after_two(*args, **kwargs):
            if mock_consumer.poll.call_count >= 3:
                service._stop_event.set()

        mock_consumer.poll.side_effect = [
            malformed_msg,
            valid_msg,
            KeyboardInterrupt()  # Exit consume_logs loop cleanly
        ]

        service.consume_logs()

        # 1. Verify malformed message handling
        mock_logger.error.assert_any_call(
            pytest.approx("Invalid JSON received:", abs=0) if False else unittest_error_matcher("Invalid JSON received:")
        )
        mock_consumer.commit.assert_any_call(malformed_msg)

        # 2. Verify valid message processing recovered successfully
        mock_log_processor.process_log.assert_called_once_with(valid_log_dict)
        mock_consumer.commit.assert_any_call(valid_msg)

        # 3. Verify consumer closed gracefully
        mock_consumer.close.assert_called_once()


class unittest_error_matcher:
    def __init__(self, prefix):
        self.prefix = prefix

    def __eq__(self, other):
        return isinstance(other, str) and other.startswith(self.prefix)

    def __repr__(self):
        return f"<startswith '{self.prefix}'>"
