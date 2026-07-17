"""
Cloud Guardian — Kafka Producer & Consumer Module.

Provides a Kafka producer for publishing normalized logs and a consumer
for reading logs from the ingestion topic.
"""

import json
from typing import Any, Callable

from app.config import get_settings
from app.logger import logger


class KafkaProducerService:
    """Kafka producer for publishing log events."""

    def __init__(self):
        self._producer = None

    def _get_producer(self):
        """Lazily initialize the Kafka producer."""
        if self._producer is None:
            try:
                from confluent_kafka import Producer

                settings = get_settings()
                self._producer = Producer({
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "client.id": "cloudguardian-producer",
                    "acks": "all",
                    "retries": 3,
                })
                logger.info("Kafka producer initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {e}")
                raise
        return self._producer

    def _delivery_callback(self, err, msg):
        """Callback for message delivery confirmation."""
        if err:
            logger.error(f"Kafka delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

    def publish(self, topic: str, key: str, value: dict[str, Any]) -> None:
        """
        Publish a message to a Kafka topic.

        Args:
            topic: Target Kafka topic.
            key: Message key (e.g., log_id).
            value: Message value as a dictionary (will be JSON serialized).
        """
        try:
            producer = self._get_producer()
            producer.produce(
                topic=topic,
                key=key.encode("utf-8"),
                value=json.dumps(value, default=str).encode("utf-8"),
                callback=self._delivery_callback,
            )
            producer.poll(0)
        except Exception as e:
            logger.error(f"Failed to publish to Kafka topic '{topic}': {e}")
            raise

    def flush(self, timeout: float = 10.0) -> int:
        """Flush pending messages."""
        if self._producer:
            return self._producer.flush(timeout)
        return 0

    def health_check(self) -> bool:
        """Check if Kafka broker is reachable."""
        try:
            producer = self._get_producer()
            # list_topics will throw if broker is unreachable
            metadata = producer.list_topics(timeout=5)
            return len(metadata.topics) >= 0
        except Exception as e:
            logger.error(f"Kafka health check failed: {e}")
            return False


class KafkaConsumerService:
    """Kafka consumer for reading log events."""

    def __init__(self):
        self._consumer = None

    def _get_consumer(self, group_id: str = "cloudguardian-consumer"):
        """Lazily initialize the Kafka consumer."""
        if self._consumer is None:
            try:
                from confluent_kafka import Consumer

                settings = get_settings()
                self._consumer = Consumer({
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "group.id": group_id,
                    "auto.offset.reset": "earliest",
                    "enable.auto.commit": True,
                })
                logger.info(f"Kafka consumer initialized (group: {group_id}).")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka consumer: {e}")
                raise
        return self._consumer

    def subscribe(self, topics: list[str]) -> None:
        """Subscribe to one or more Kafka topics."""
        consumer = self._get_consumer()
        consumer.subscribe(topics)
        logger.info(f"Subscribed to Kafka topics: {topics}")

    def consume(self, callback: Callable[[dict[str, Any]], None], max_messages: int = 100, timeout: float = 1.0) -> int:
        """
        Consume messages from subscribed topics and process with callback.

        Args:
            callback: Function to call with each deserialized message.
            max_messages: Maximum number of messages to consume in one batch.
            timeout: Polling timeout in seconds.

        Returns:
            Number of messages consumed.
        """
        consumer = self._get_consumer()
        consumed = 0

        for _ in range(max_messages):
            msg = consumer.poll(timeout)
            if msg is None:
                break
            if msg.error():
                logger.error(f"Kafka consumer error: {msg.error()}")
                continue

            try:
                value = json.loads(msg.value().decode("utf-8"))
                callback(value)
                consumed += 1
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode Kafka message: {e}")
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")

        return consumed

    def close(self) -> None:
        """Close the consumer connection."""
        if self._consumer:
            self._consumer.close()
            self._consumer = None
            logger.info("Kafka consumer closed.")


# Singleton instances
kafka_producer = KafkaProducerService()
kafka_consumer = KafkaConsumerService()
