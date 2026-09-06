"""
AWS SQS Consumer Service
========================

Polls the CloudGuardianCloudTrailQueue SQS queue for real-time AWS
CloudTrail events delivered by EventBridge, and forwards each event
into the existing Kafka cloud_logs topic so the rest of the
CloudGuardian pipeline (Normalizer -> Correlation -> Risk -> Alert Engine
-> OpenSearch) can process them without any modification.

Flow:
    AWS Activity
        -> CloudTrail
        -> EventBridge rule (aws.* / AWS API Call via CloudTrail)
        -> SQS: CloudGuardianCloudTrailQueue
        -> THIS SERVICE (background thread)
        -> existing kafka_producer (confluent_kafka.Producer)
        -> existing cloud_logs Kafka topic
        -> existing KafkaConsumerService / LogProcessor / Pipeline
        -> OpenSearch / Dashboard

Design decisions:
-   Long-polling (WaitTimeSeconds=20) avoids unnecessary ReceiveMessage
    API calls when the queue is empty; combined with MaxNumberOfMessages=10
    it batches up to 10 messages per call, minimising cost.
-   SQS message is deleted ONLY after Kafka delivery is confirmed.
-   On Kafka failure the message is NOT deleted; SQS re-delivers it
    automatically after the queue visibility timeout (30 s).
-   Malformed JSON is deleted immediately — it can never be processed
    regardless of retries and would block the queue indefinitely.
-   All AWS credentials are read from the existing Settings/.env system.
    Credentials are never logged.
-   The boto3 client is created inside start() (not at import time) so
    that the Uvicorn --reload parent process (which imports the module
    but never calls startup_event) does not hold an SQS client.
-   start() guards against double-starts with an is_alive() check, so
    calling it more than once (e.g. due to reload) is safe.
-   The polling thread is a daemon thread: if FastAPI exits without
    calling shutdown_event, the thread is reaped automatically.
"""

import json
import threading
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings
from app.kafka.producer import kafka_producer
from app.logger import logger
from app.utils.redaction import redact_sensitive_data

# Load the singleton settings object (already cached via @lru_cache)
settings = get_settings()


class AWSSQSConsumer:
    """
    Background SQS consumer.

    Instantiated once at module level (singleton).  Call start() from
    FastAPI startup_event() and stop() from FastAPI shutdown_event().
    """

    def __init__(self) -> None:
        self._stop_event: threading.Event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._sqs = None  # Created lazily in start() — not at import time

        # Check configuration at construction time so warnings appear early,
        # but do NOT open any network connections here.
        if not settings.AWS_SQS_QUEUE_URL:
            logger.warning(
                "AWS_SQS_QUEUE_URL is not configured. "
                "SQS consumer will not start."
            )
            self._configured = False
            return

        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            logger.warning(
                "AWS credentials (AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY) "
                "are not configured. SQS consumer will not start."
            )
            self._configured = False
            return

        self._configured = True
        self._queue_url: str = settings.AWS_SQS_QUEUE_URL

        logger.info(
            f"AWSSQSConsumer configured. "
            f"Queue: {self._queue_url} | Region: {settings.AWS_REGION}"
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the SQS polling loop in a background daemon thread.

        Called once from FastAPI startup_event().  Safe to call more than
        once — if the thread is already running it will not be duplicated.
        """
        if not self._configured:
            logger.warning(
                "AWSSQSConsumer is not configured. Skipping start."
            )
            return

        # Guard against double-start (e.g. uvicorn --reload edge cases)
        if self._thread is not None and self._thread.is_alive():
            logger.warning(
                "AWSSQSConsumer.start() called but thread is already running. "
                "Ignoring duplicate start."
            )
            return

        # Create the boto3 SQS client here (runtime), not at import time.
        # This keeps the Uvicorn reloader parent process free of AWS clients.
        # Credentials are read from Settings which reads from .env.
        # They are NEVER logged or printed.
        try:
            self._sqs = boto3.client(
                "sqs",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
        except Exception as client_err:
            logger.error(
                f"Failed to create boto3 SQS client: {client_err}. "
                "SQS consumer will not start."
            )
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._polling_loop,
            name="SQSConsumerThread",
            daemon=True,  # Reaped automatically if FastAPI exits without shutdown
        )
        self._thread.start()
        logger.info("AWS SQS consumer started (background thread).")

    def stop(self) -> None:
        """
        Signal the polling loop to exit cleanly and wait for it to finish.

        Called from FastAPI shutdown_event().  Returns after the thread
        stops or after a 25-second safety timeout (the long-poll is 20 s
        so the thread should always finish within that window).
        """
        if self._thread is None or not self._thread.is_alive():
            return

        logger.info("AWS SQS consumer stopping...")
        self._stop_event.set()

        # Wait up to 25 s — covers the full 20 s long-poll window plus margin
        self._thread.join(timeout=25)

        if self._thread.is_alive():
            logger.warning(
                "AWS SQS consumer thread did not stop within 25 s. "
                "It will be reaped as a daemon thread when the process exits."
            )
        else:
            logger.info("AWS SQS consumer stopped cleanly.")

    # ------------------------------------------------------------------
    # Internal polling loop — runs inside the daemon thread
    # ------------------------------------------------------------------

    def _polling_loop(self) -> None:
        """
        Long-poll the SQS queue in a loop until stop() sets the stop event.

        AWS/network errors cause a 10-second back-off before retrying.
        Unexpected errors are also caught so the consumer never crashes FastAPI.
        """
        logger.info(
            "SQS polling loop started. "
            "WaitTimeSeconds=20 (long-poll) | MaxNumberOfMessages=10 (batch)."
        )

        while not self._stop_event.is_set():
            try:
                self._poll_once()

            except (BotoCoreError, ClientError) as aws_err:
                # Transient AWS/network errors — back off before retrying
                logger.error(
                    f"AWS/SQS error during polling: {aws_err}. "
                    "Backing off 10 seconds before retry."
                )
                # Use wait() so the stop signal interrupts the sleep
                self._stop_event.wait(timeout=10)

            except Exception as unexpected_err:
                # Catch-all: log and continue — the consumer must not
                # bring down the FastAPI process
                logger.error(
                    f"Unexpected error in SQS polling loop: {unexpected_err}. "
                    "Backing off 10 seconds before retry."
                )
                self._stop_event.wait(timeout=10)

        logger.info("SQS polling loop exited cleanly.")

    def _poll_once(self) -> None:
        """
        Issue one long-poll ReceiveMessage call and process every returned message.
        """
        response = self._sqs.receive_message(
            QueueUrl=self._queue_url,
            MaxNumberOfMessages=10,   # Batch up to 10 messages per API call
            WaitTimeSeconds=20,       # Long-poll: block up to 20 s if queue empty
            AttributeNames=["All"],
            MessageAttributeNames=["All"],
        )

        messages = response.get("Messages", [])

        if not messages:
            # Queue was empty for the full 20-second poll window
            return

        logger.info(f"Received {len(messages)} SQS message(s).")

        for message in messages:
            self._process_message(message)

    def _process_message(self, message: dict) -> None:
        """
        Parse one SQS message, publish it to Kafka, then delete it from SQS.

        The SQS message is deleted ONLY after Kafka confirms delivery.
        If delivery fails the message is left in-flight and SQS re-delivers
        it after the queue's visibility timeout (30 s).
        """
        receipt_handle: str = message.get("ReceiptHandle", "")
        message_id: str = message.get("MessageId", "unknown")

        # ------------------------------------------------------------------
        # Step 1: Parse the SQS message body as JSON
        # ------------------------------------------------------------------
        try:
            body = json.loads(message["Body"])
        except (json.JSONDecodeError, KeyError) as json_err:
            # Malformed JSON cannot be fixed by retrying.  Delete the message
            # so it does not block the queue and incur repeated visibility
            # timeout cycles (and unnecessary SQS API calls).
            logger.error(
                f"SQS message {message_id} has an invalid JSON body: {json_err}. "
                "Deleting malformed message (retry cannot fix this)."
            )
            self._delete_message(receipt_handle, message_id)
            return

        # ------------------------------------------------------------------
        # Step 2: Build the event dict to forward to Kafka.
        # Extract the CloudTrail event from the EventBridge envelope and
        # annotate it with provider="AWS" so the existing normalizer factory
        # routes it to AWSNormalizer, exactly as the /logs/ API route does.
        # ------------------------------------------------------------------
        # Work on a copy so we do not mutate the parsed body
        event_detail: dict = dict(body.get("detail", {}))

        # "provider" is what incident_pipeline uses to select the normalizer
        event_detail["provider"] = "AWS"

        # Apply redaction before logging or further processing
        sanitized_detail = redact_sensitive_data(event_detail)

        # Preserve top-level EventBridge envelope fields for context
        event_detail["eventbridge_source"] = body.get("source", "")
        event_detail["eventbridge_account"] = body.get("account", "")
        event_detail["eventbridge_region"] = body.get("region", "")
        event_detail["eventbridge_time"] = body.get("time", "")

        event_name: str = sanitized_detail.get("eventName", "UnknownEvent")
        event_source: str = body.get("source", "unknown")

        logger.info(
            f"SQS message {message_id} | "
            f"AWS source: {event_source} | CloudTrail event: {event_name} | "
            f"Sanitized Event: {sanitized_detail}"
        )

        # ------------------------------------------------------------------
        # Step 3: Publish to Kafka and confirm delivery before deleting.
        #
        # kafka_producer.send_log() catches its own exceptions internally
        # (see kafka/producer.py) and does not re-raise, so we cannot rely
        # on it to signal failure.  Instead we call the underlying
        # confluent_kafka.Producer directly with a local delivery callback,
        # then flush() with a timeout and inspect the remaining-message count.
        #
        # flush(timeout) returns the number of messages still in the local
        # queue after the timeout.  0 means all messages were delivered.
        # > 0 means at least one delivery failed or timed out.
        # ------------------------------------------------------------------
        delivery_error: list = []  # Mutable container for callback to write into

        def _delivery_callback(err, msg):
            if err is not None:
                delivery_error.append(err)
                logger.error(
                    f"Kafka delivery failed for SQS message {message_id}: {err}"
                )
            else:
                logger.info(
                    f"SQS message {message_id} delivered to Kafka topic "
                    f"'{msg.topic()}' [partition {msg.partition()}] "
                    f"offset {msg.offset()}."
                )

        try:
            kafka_producer.producer.produce(
                topic=settings.KAFKA_TOPIC,
                value=json.dumps(event_detail),
                callback=_delivery_callback,
            )
            # flush() blocks until all queued messages are delivered or the
            # timeout expires.  Returns the number still in the queue.
            remaining = kafka_producer.producer.flush(timeout=10)

        except Exception as kafka_err:
            # Producer itself raised (e.g. buffer full, broker unreachable)
            logger.error(
                f"Kafka producer raised an exception for SQS message "
                f"{message_id}: {kafka_err}. "
                "SQS message will NOT be deleted — it will be retried."
            )
            return

        if remaining > 0 or delivery_error:
            # flush() timed out without delivering, or callback reported error
            logger.error(
                f"Kafka delivery NOT confirmed for SQS message {message_id} "
                f"(remaining={remaining}, errors={len(delivery_error)}). "
                "SQS message will NOT be deleted — it will be retried."
            )
            return

        # ------------------------------------------------------------------
        # Step 4: Delivery confirmed — now safe to delete the SQS message.
        # ------------------------------------------------------------------
        self._delete_message(receipt_handle, message_id)

    def _delete_message(self, receipt_handle: str, message_id: str) -> None:
        """
        Delete one SQS message by its receipt handle.

        A delete failure is non-fatal: the message will become visible again
        after the visibility timeout and be reprocessed.  At worst, Kafka
        receives a duplicate event — acceptable for a best-effort SIEM.
        """
        try:
            self._sqs.delete_message(
                QueueUrl=self._queue_url,
                ReceiptHandle=receipt_handle,
            )
            logger.info(
                f"SQS message {message_id} deleted from queue successfully."
            )
        except (BotoCoreError, ClientError) as delete_err:
            logger.error(
                f"Failed to delete SQS message {message_id}: {delete_err}. "
                "Message will become visible again after the visibility timeout."
            )


# ---------------------------------------------------------------------------
# Module-level singleton — imported by main.py.
# __init__ validates configuration but opens NO network connections.
# start() is called from FastAPI startup_event() (worker process only).
# ---------------------------------------------------------------------------
sqs_consumer = AWSSQSConsumer()
