import json

from confluent_kafka import Consumer

from app.config import get_settings
from app.logger import logger
from app.parser.parser import log_parser
from app.normalizer.normalizer import log_normalizer

settings = get_settings()


class KafkaConsumerService:
    """
    Kafka Consumer responsible for receiving cloud logs,
    parsing them, and normalizing them before passing them
    to the next stage of the pipeline.
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

                try:
                    # Step 1: Decode Kafka message
                    log_data = json.loads(
                        message.value().decode("utf-8")
                    )

                    logger.info(f"Received Log: {log_data}")

                    # Step 2: Parse the log
                    parsed_log = log_parser.parse(log_data)

                    logger.info(f"Parsed Log: {parsed_log}")

                    # Step 3: Normalize the parsed log
                    normalized_log = log_normalizer.normalize(parsed_log)

                    logger.info(f"Normalized Log: {normalized_log}")

                    # Step 4:
                    # This normalized log will later be sent
                    # to the Correlation Engine.

                except json.JSONDecodeError as e:

                    logger.error(f"Invalid JSON received: {e}")

                except Exception as e:

                    logger.error(f"Error processing log: {e}")

        except KeyboardInterrupt:

            logger.info("Kafka Consumer stopped by user.")

        finally:

            self.consumer.close()
            logger.info("Kafka Consumer closed successfully.")


kafka_consumer = KafkaConsumerService()