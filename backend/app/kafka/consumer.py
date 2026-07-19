import json

from confluent_kafka import Consumer

from app.config import get_settings
from app.logger import logger
from app.parser.parser import log_parser

settings = get_settings()


class KafkaConsumerService:
    """
    Kafka Consumer responsible for receiving cloud logs
    from the Kafka topic.
    """

    def __init__(self):

        self.consumer = Consumer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "cloudguardian-consumer-group",
                "auto.offset.reset": "earliest",
            }
        )

        self.consumer.subscribe([settings.KAFKA_TOPIC])

        logger.info("Kafka Consumer initialized successfully.")
        logger.info(f"Subscribed to topic: {settings.KAFKA_TOPIC}")

    def consume_logs(self):

        logger.info("Waiting for incoming cloud logs...")

        try:

            while True:

                message = self.consumer.poll(timeout=1.0)

                if message is None:
                    continue

                if message.error():
                    logger.error(f"Consumer Error: {message.error()}")
                    continue

                log_data = json.loads(
                    message.value().decode("utf-8")
                )

                try:
                    parsed_log = log_parser.parse(log_data)
                    logger.info(f"Parsed Log: {parsed_log}")
                except Exception as e:
                    logger.error(f"Parser Error: {e}")

        except KeyboardInterrupt:

            logger.info("Kafka Consumer stopped by user.")

        finally:

            self.consumer.close()
            logger.info("Kafka Consumer closed successfully.")


kafka_consumer = KafkaConsumerService()