import json

from confluent_kafka import Producer

from app.config import get_settings
from app.logger import logger

# Load application settings
settings = get_settings()


class KafkaProducerService:
    """
    Kafka Producer Service

    Responsible for sending cloud security logs
    to the configured Kafka topic.
    """

    def __init__(self):
        self.producer = Producer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS
            }
        )

        logger.info("Kafka Producer initialized successfully.")

    def delivery_report(self, err, msg):
        """
        Callback function executed after Kafka
        attempts to deliver a message.
        """

        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.info(
                f"Message delivered to "
                f"{msg.topic()} "
                f"[Partition {msg.partition()}] "
                f"Offset {msg.offset()}"
            )

    def send_log(self, log_data: dict):
        """
        Sends a cloud log to Kafka.
        """

        try:
            self.producer.produce(
                topic=settings.KAFKA_TOPIC,
                value=json.dumps(log_data),
                callback=self.delivery_report
            )

            # Trigger delivery callbacks
            self.producer.poll(0)

            logger.info("Log queued for Kafka delivery.")

        except Exception as e:
            logger.error(f"Error sending log to Kafka: {e}")

    def flush(self):
        """
        Flush pending Kafka messages.
        """

        self.producer.flush()
        logger.info("Kafka Producer flushed successfully.")


# Singleton Producer Instance
kafka_producer = KafkaProducerService()