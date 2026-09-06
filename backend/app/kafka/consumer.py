import json
import threading
from typing import Optional

from confluent_kafka import Consumer

from app.config import get_settings
from app.logger import logger
from app.services.log_processor import log_processor
from app.utils.redaction import redact_sensitive_data

settings = get_settings()


class KafkaConsumerService:
    """
    Kafka Consumer responsible for receiving cloud logs,
    parsing them, and normalizing them before passing them
    to the next stage of the pipeline.
    """

    def __init__(self):
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._configured = True
        self.consumer = None
        
        if not settings.KAFKA_BOOTSTRAP_SERVERS:
            logger.warning("KAFKA_BOOTSTRAP_SERVERS not configured. Consumer will not start.")
            self._configured = False
            return

        logger.info("Kafka Consumer configured.")

    def start(self) -> None:
        """Start consumer background thread."""
        if not self._configured:
            return
        if self._thread is not None and self._thread.is_alive():
            return
            
        try:
            self.consumer = Consumer(
                {
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "group.id": "cloudguardian-consumer-group",
                    "auto.offset.reset": "earliest",
                    "enable.auto.commit": False,
                }
            )
            self.consumer.subscribe([settings.KAFKA_TOPIC])
            logger.info("Kafka Consumer initialized successfully.")
            logger.info(f"Subscribed to topic: {settings.KAFKA_TOPIC}")
        except Exception as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self.consume_logs,
            name="KafkaConsumerThread",
            daemon=True,
        )
        self._thread.start()
        logger.info("Kafka consumer started (background thread).")

    def stop(self) -> None:
        """Stop consumer gracefully."""
        if self._thread is None or not self._thread.is_alive():
            return
        logger.info("Kafka consumer stopping...")
        self._stop_event.set()
        self._thread.join(timeout=10)

    def consume_logs(self):

        logger.info("Waiting for incoming cloud logs...")

        try:
            while not self._stop_event.is_set():
                message = self.consumer.poll(timeout=1.0)

                if message is None:
                    continue

                if message.error():
                    logger.error(f"Consumer Error: {message.error()}")
                    continue

                try:
                    # Step 1: Decode Kafka message
                    log_data = json.loads(message.value().decode("utf-8"))

                    # Log a sanitized copy — credentials are never printed
                    logger.info(f"Received Log: {redact_sensitive_data(log_data)}")

                    # Step 2: Route to LogProcessor
                    log_processor.process_log(log_data)

                    # Step 3: Explicitly commit the message offset after successful processing
                    self.consumer.commit(message)

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    # Cannot retry invalid JSON, so commit to skip
                    self.consumer.commit(message)

                except Exception as e:
                    logger.error(f"Error processing log: {e}")
                    # Do NOT commit on LogProcessor failure, allowing potential retry/redelivery

        except KeyboardInterrupt:
            logger.info("Kafka Consumer stopped by user.")

        finally:
            self.consumer.close()
            logger.info("Kafka Consumer closed successfully.")


kafka_consumer = KafkaConsumerService()