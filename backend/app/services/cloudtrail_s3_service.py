"""
CloudTrail S3 Log Ingestion Service
===================================

Periodically scans the central CloudTrail S3 bucket for multi-region
management event logs (.json.gz), downloads and safely decompresses them,
extracts individual event records, attaches ingestion metadata, and forwards
them into the existing CloudGuardian Kafka pipeline (cloud_logs topic).

Key Capabilities:
- Multi-Region support: Automatically discovers logs across all AWS regions
  under the account prefix (e.g., eu-north-1, us-east-1, ap-south-1).
- Restart-safe checkpointing: Remembers processed files via OpenSearch
  (cloudguardian_s3_checkpoints index) with resilient local cache fallback.
- Event deduplication: Tracks individual eventIDs to avoid generating duplicate
  security incidents.
- Delivery confirmation: Marks files as processed only after Kafka delivery
  is confirmed.
- Bounded retries: Limits retries on transient errors to 3 attempts, preventing
  infinite retry loops.
- Error resilience: Handles corrupt gzip, malformed JSON, empty files, truncated
  downloads, and Kafka failures gracefully without terminating the scheduler.
- Zero credential leakage: Never logs AWS keys, tokens, or sensitive records.
"""

import gzip
import io
import json
import threading
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import get_settings
from app.kafka.producer import kafka_producer
from app.logger import logger
from app.storage.s3_checkpoint_repository import s3_checkpoint_repository
from app.utils.redaction import redact_sensitive_data

settings = get_settings()

MAX_FILE_RETRIES = 3
MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024  # 50 MB safety cap against decompression bombs


class CloudTrailS3IngestionService:
    """
    Periodic S3 CloudTrail ingestion service.

    Runs as a background daemon thread integrated into the FastAPI lifespan.
    Can also be invoked directly via scan_and_process() for manual/test triggers.
    """

    def __init__(
        self,
        checkpoint_repo=None,
        s3_client=None,
    ) -> None:
        self._stop_event: threading.Event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._s3_client = s3_client  # Can be injected for tests
        self._checkpoint_repo = checkpoint_repo or s3_checkpoint_repository

        # Runtime scan metrics
        self._stats_lock = threading.Lock()
        self._last_successful_scan_time: Optional[str] = None
        self._total_scans_completed: int = 0
        self._total_files_discovered: int = 0
        self._total_files_processed: int = 0
        self._total_historical_skipped: int = 0
        self._total_records_parsed: int = 0
        self._total_records_published: int = 0
        self._total_duplicates_skipped: int = 0
        self._total_kafka_failures: int = 0
        self._total_file_failures: int = 0

    # ------------------------------------------------------------------
    # Public Lifecycle Interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the periodic S3 ingestion loop in a background daemon thread.
        Guards against duplicate starts and respects configuration enablement.
        """
        if not settings.CLOUDTRAIL_S3_INGESTION_ENABLED:
            logger.info(
                "CloudTrail S3 ingestion is disabled by configuration "
                "(CLOUDTRAIL_S3_INGESTION_ENABLED=False). Ingestion will not start."
            )
            return

        if not settings.CLOUDTRAIL_S3_BUCKET:
            logger.warning(
                "CLOUDTRAIL_S3_BUCKET is not configured. "
                "CloudTrail S3 ingestion will not start."
            )
            return

        if self._thread is not None and self._thread.is_alive():
            logger.warning(
                "CloudTrailS3IngestionService.start() called but thread is already running. "
                "Ignoring duplicate start."
            )
            return

        # Ensure S3 client is initialized
        if self._s3_client is None:
            self._s3_client = self._create_s3_client()
            if self._s3_client is None:
                logger.error(
                    "Failed to initialize S3 client. CloudTrail S3 ingestion will not start."
                )
                return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._scheduler_loop,
            name="CloudTrailS3IngestionThread",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            f"CloudTrail S3 ingestion service started (background thread). "
            f"Bucket: {settings.CLOUDTRAIL_S3_BUCKET} | "
            f"Prefix: {settings.CLOUDTRAIL_S3_PREFIX} | "
            f"Interval: {settings.CLOUDTRAIL_S3_SCAN_INTERVAL_SECONDS}s"
        )

    def stop(self) -> None:
        """
        Signal the scheduler thread to stop and wait for completion.
        """
        if self._thread is None or not self._thread.is_alive():
            return

        logger.info("CloudTrail S3 ingestion service stopping...")
        self._stop_event.set()
        self._thread.join(timeout=15)

        if self._thread.is_alive():
            logger.warning(
                "CloudTrail S3 ingestion thread did not terminate within 15s. "
                "It will be reaped upon process exit."
            )
        else:
            logger.info("CloudTrail S3 ingestion service stopped cleanly.")

    def get_stats(self) -> Dict[str, Any]:
        """Return runtime observability statistics."""
        with self._stats_lock:
            return {
                "enabled": settings.CLOUDTRAIL_S3_INGESTION_ENABLED,
                "bucket": settings.CLOUDTRAIL_S3_BUCKET,
                "prefix": settings.CLOUDTRAIL_S3_PREFIX,
                "aws_profile": settings.CLOUDTRAIL_S3_AWS_PROFILE,
                "backfill_enabled": settings.CLOUDTRAIL_S3_BACKFILL_ENABLED,
                "lookback_hours": settings.CLOUDTRAIL_S3_LOOKBACK_HOURS,
                "scan_interval_seconds": settings.CLOUDTRAIL_S3_SCAN_INTERVAL_SECONDS,
                "last_successful_scan_time": self._last_successful_scan_time,
                "total_scans_completed": self._total_scans_completed,
                "total_files_discovered": self._total_files_discovered,
                "total_files_processed": self._total_files_processed,
                "total_historical_skipped": self._total_historical_skipped,
                "total_records_parsed": self._total_records_parsed,
                "total_records_published": self._total_records_published,
                "total_duplicates_skipped": self._total_duplicates_skipped,
                "total_kafka_failures": self._total_kafka_failures,
                "total_file_failures": self._total_file_failures,
            }

    # ------------------------------------------------------------------
    # Scheduler Loop
    # ------------------------------------------------------------------

    def _scheduler_loop(self) -> None:
        """Periodic background execution loop."""
        interval = max(1, settings.CLOUDTRAIL_S3_SCAN_INTERVAL_SECONDS)
        logger.info(f"S3 ingestion scheduler loop running. Scan interval: {interval}s.")

        while not self._stop_event.is_set():
            try:
                self.scan_and_process()
            except Exception as e:
                logger.error(f"Unhandled exception during S3 scan cycle: {e}")

            # Wait for next interval or early exit on stop event
            self._stop_event.wait(timeout=interval)

        logger.info("S3 ingestion scheduler loop exited.")

    # ------------------------------------------------------------------
    # Core Scan & Ingestion Logic
    # ------------------------------------------------------------------

    def scan_and_process(self) -> Dict[str, Any]:
        """
        Execute a single scan cycle over the configured S3 bucket and prefix.

        Discovers all CloudTrail .json.gz objects across all regions, filters
        out already processed objects, processes new objects, publishes events
        to Kafka, and updates checkpoints.
        """
        scan_start_time = datetime.now(timezone.utc).isoformat()
        bucket = settings.CLOUDTRAIL_S3_BUCKET
        prefix = settings.CLOUDTRAIL_S3_PREFIX
        max_files = settings.CLOUDTRAIL_S3_MAX_FILES_PER_SCAN

        backfill_enabled = bool(settings.CLOUDTRAIL_S3_BACKFILL_ENABLED)
        lookback_hours = int(settings.CLOUDTRAIL_S3_LOOKBACK_HOURS)
        start_date_str = settings.CLOUDTRAIL_S3_START_DATE
        now = datetime.now(timezone.utc)

        start_cutoff = None
        if start_date_str:
            try:
                start_cutoff = datetime.fromisoformat(start_date_str.replace("Z", "+00:00"))
                if start_cutoff.tzinfo is None:
                    start_cutoff = start_cutoff.replace(tzinfo=timezone.utc)
            except Exception as ex:
                logger.warning(f"Could not parse CLOUDTRAIL_S3_START_DATE '{start_date_str}': {ex}")

        if backfill_enabled:
            mode = "HISTORICAL_BACKFILL"
            cutoff_time = start_cutoff
            logger.info(
                f"Historical backfill mode active (CLOUDTRAIL_S3_BACKFILL_ENABLED=True). "
                f"Processing all eligible objects{f' from {start_cutoff.isoformat()}' if start_cutoff else ''}."
            )
        else:
            mode = "LIVE_INGESTION"
            live_cutoff = now - timedelta(hours=lookback_hours)
            if start_cutoff and start_cutoff > live_cutoff:
                cutoff_time = start_cutoff
            else:
                cutoff_time = live_cutoff
            logger.info(
                f"Live ingestion mode active (CLOUDTRAIL_S3_BACKFILL_ENABLED=False). "
                f"Processing objects modified within the last {lookback_hours}h (cutoff: {cutoff_time.isoformat()})."
            )

        logger.info(
            f"--- Starting CloudTrail S3 Scan [{mode}] | Bucket: {bucket} | Prefix: {prefix} ---"
        )

        cycle_stats = {
            "mode": mode,
            "discovered_files": 0,
            "already_processed_files": 0,
            "historical_skipped_files": 0,
            "new_objects_accepted": 0,
            "files_attempted": 0,
            "files_succeeded": 0,
            "files_failed": 0,
            "records_parsed": 0,
            "records_published": 0,
            "duplicates_skipped": 0,
            "kafka_failures": 0,
        }

        # 1. Discover objects via pagination
        try:
            discovered_objects = self._discover_objects(bucket, prefix)
        except Exception as e:
            logger.error(f"Failed to list objects in bucket '{bucket}' with prefix '{prefix}': {e}")
            return cycle_stats

        cycle_stats["discovered_files"] = len(discovered_objects)
        logger.info(f"Discovered {len(discovered_objects)} candidate log file(s).")

        # 2. Filter already processed, retry-exhausted, or historical files (if live mode)
        files_to_process = []
        for obj in discovered_objects:
            key = obj["Key"]
            etag = obj.get("ETag", "").strip('"')

            if self._checkpoint_repo.is_file_processed(key, etag):
                cycle_stats["already_processed_files"] += 1
                continue

            retry_count = self._checkpoint_repo.get_retry_count(key)
            if retry_count >= MAX_FILE_RETRIES:
                logger.warning(
                    f"Skipping S3 object '{key}' — retry limit ({MAX_FILE_RETRIES}) reached."
                )
                cycle_stats["already_processed_files"] += 1
                continue

            # In live ingestion mode, skip files older than the lookback window unless backfill is explicitly enabled
            if cutoff_time is not None:
                last_mod = obj.get("LastModified")
                if isinstance(last_mod, str):
                    try:
                        last_mod = datetime.fromisoformat(last_mod.replace("Z", "+00:00"))
                    except Exception:
                        last_mod = None
                if isinstance(last_mod, datetime):
                    if last_mod.tzinfo is None:
                        last_mod = last_mod.replace(tzinfo=timezone.utc)
                    if last_mod < cutoff_time:
                        cycle_stats["historical_skipped_files"] += 1
                        logger.debug(
                            f"Skipping historical S3 object '{key}' "
                            f"(modified {last_mod.isoformat()} < cutoff {cutoff_time.isoformat()}). "
                            "Enable CLOUDTRAIL_S3_BACKFILL_ENABLED to backfill historical objects."
                        )
                        continue

            files_to_process.append(obj)
            if len(files_to_process) >= max_files:
                logger.info(
                    f"Reached max files per scan limit ({max_files}). "
                    "Remaining files will be processed in subsequent scans."
                )
                break

        cycle_stats["new_objects_accepted"] = len(files_to_process)
        logger.info(
            f"Scan summary [{mode}]: {cycle_stats['discovered_files']} discovered, "
            f"{cycle_stats['already_processed_files']} already processed, "
            f"{cycle_stats['historical_skipped_files']} historical skipped, "
            f"{len(files_to_process)} new object(s) accepted for ingestion."
        )

        # 3. Process each candidate file
        for obj in files_to_process:
            if self._stop_event.is_set():
                logger.info("Scan interrupted by shutdown signal.")
                break

            key = obj["Key"]
            etag = obj.get("ETag", "").strip('"')
            version_id = obj.get("VersionId")
            cycle_stats["files_attempted"] += 1

            try:
                res = self._process_file(bucket, key, etag, version_id)
                cycle_stats["records_parsed"] += res.get("records_parsed", 0)
                if res["success"]:
                    cycle_stats["files_succeeded"] += 1
                    cycle_stats["records_published"] += res["records_published"]
                    cycle_stats["duplicates_skipped"] += res["duplicates_skipped"]
                else:
                    cycle_stats["files_failed"] += 1
                    cycle_stats["kafka_failures"] += res.get("kafka_failures", 0)
            except Exception as file_err:
                cycle_stats["files_failed"] += 1
                logger.error(f"Unexpected error processing S3 file '{key}': {file_err}")
                self._checkpoint_repo.record_file_failure(
                    key, bucket, str(file_err), etag=etag, version_id=version_id
                )

        scan_end_time = datetime.now(timezone.utc).isoformat()
        with self._stats_lock:
            self._total_scans_completed += 1
            self._last_successful_scan_time = scan_end_time
            self._total_files_discovered += cycle_stats["discovered_files"]
            self._total_files_processed += cycle_stats["files_succeeded"]
            self._total_historical_skipped += cycle_stats["historical_skipped_files"]
            self._total_records_parsed += cycle_stats["records_parsed"]
            self._total_records_published += cycle_stats["records_published"]
            self._total_duplicates_skipped += cycle_stats["duplicates_skipped"]
            self._total_kafka_failures += cycle_stats["kafka_failures"]
            self._total_file_failures += cycle_stats["files_failed"]

        logger.info(
            f"--- Completed CloudTrail S3 Scan [{mode}] | "
            f"Discovered: {cycle_stats['discovered_files']} | "
            f"Accepted: {cycle_stats['new_objects_accepted']} | "
            f"Already Processed: {cycle_stats['already_processed_files']} | "
            f"Historical Skipped: {cycle_stats['historical_skipped_files']} | "
            f"Attempted: {cycle_stats['files_attempted']} | "
            f"Succeeded: {cycle_stats['files_succeeded']} | "
            f"Failed: {cycle_stats['files_failed']} | "
            f"Parsed: {cycle_stats['records_parsed']} | "
            f"Published: {cycle_stats['records_published']} | "
            f"Duplicates Skipped: {cycle_stats['duplicates_skipped']} ---"
        )

        return cycle_stats

    # ------------------------------------------------------------------
    # Object Discovery & Regional Handling
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_region_from_key(key: str) -> Optional[str]:
        """
        Extract AWS region from standard CloudTrail S3 key:
        AWSLogs/<account_id>/CloudTrail/<region>/<year>/<month>/<day>/...
        """
        if not key:
            return None
        parts = key.split("/")
        for i, part in enumerate(parts):
            if part == "CloudTrail" and i + 1 < len(parts):
                candidate = parts[i + 1]
                if candidate and not candidate.isdigit() and len(candidate) >= 4:
                    return candidate
        return None

    def discover_regions(self, bucket: str, prefix: str) -> List[str]:
        """
        Discover regional subdirectories under the CloudTrail prefix using Delimiter='/'.
        Returns a sorted list of discovered regions (e.g. ['ap-south-1', 'eu-north-1', ...]).
        """
        normalized_prefix = prefix if prefix.endswith("/") else f"{prefix}/"
        regions = []
        try:
            paginator = self._s3_client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket, Prefix=normalized_prefix, Delimiter="/"):
                for cp in page.get("CommonPrefixes", []):
                    p_str = cp.get("Prefix", "").rstrip("/")
                    region_name = p_str.split("/")[-1]
                    if region_name and not region_name.isdigit() and region_name != "CloudTrail":
                        regions.append(region_name)
        except Exception as ex:
            logger.warning(f"Failed to dynamically discover regional prefixes in s3://{bucket}/{prefix}: {ex}")
        return sorted(list(set(regions)))

    def _discover_objects(self, bucket: str, prefix: str) -> List[Dict[str, Any]]:
        """
        List all CloudTrail .json.gz objects across target regions.
        Supports regional discovery based on CLOUDTRAIL_S3_REGIONS or full discovery.
        Preserves Mumbai (ap-south-1) and global events while ensuring eu-north-1
        and other configured regions are discovered.
        """
        configured_regions = settings.CLOUDTRAIL_S3_REGIONS
        target_prefixes = []

        normalized_prefix = prefix if prefix.endswith("/") else f"{prefix}/"

        if configured_regions and configured_regions.strip():
            regions = [r.strip() for r in configured_regions.split(",") if r.strip()]
            for r in regions:
                target_prefixes.append(f"{normalized_prefix}{r}/")
            logger.info(f"Scanning {len(target_prefixes)} configured region prefix(es): {regions}")
        else:
            target_prefixes.append(normalized_prefix)

        discovered = []
        paginator = self._s3_client.get_paginator("list_objects_v2")

        for target_pfx in target_prefixes:
            for page in paginator.paginate(Bucket=bucket, Prefix=target_pfx):
                contents = page.get("Contents", [])
                for item in contents:
                    key = item.get("Key", "")
                    if key.endswith(".json.gz"):
                        discovered.append(item)

        # Sort chronologically by LastModified if available so older logs process first
        discovered.sort(key=lambda x: str(x.get("LastModified", "")))
        return discovered

    # ------------------------------------------------------------------
    # Single File Processing Pipeline
    # ------------------------------------------------------------------

    def _process_file(
        self,
        bucket: str,
        key: str,
        etag: str,
        version_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Download, decompress, parse, validate, and publish records from one S3 file.
        Marks file as processed ONLY upon confirmed delivery of all records.
        """
        logger.info(f"Processing S3 CloudTrail log: s3://{bucket}/{key}")

        # Step 1: Download object
        try:
            response = self._s3_client.get_object(Bucket=bucket, Key=key)
            raw_compressed = response["Body"].read()
        except (BotoCoreError, ClientError) as aws_err:
            retries = self._checkpoint_repo.record_file_failure(
                key, bucket, f"AWS S3 download error: {aws_err}", etag, version_id
            )
            logger.error(
                f"Failed to download s3://{bucket}/{key}: {aws_err} (attempt {retries}/{MAX_FILE_RETRIES})"
            )
            return {"success": False, "records_parsed": 0, "records_published": 0, "duplicates_skipped": 0}

        # Step 2: Safe gzip decompression
        try:
            decompressed_bytes = self._decompress_gzip_safely(raw_compressed)
        except Exception as decomp_err:
            retries = self._checkpoint_repo.record_file_failure(
                key, bucket, f"Gzip decompression error: {decomp_err}", etag, version_id
            )
            logger.error(
                f"Malformed/corrupt gzip in s3://{bucket}/{key}: {decomp_err} "
                f"(attempt {retries}/{MAX_FILE_RETRIES})"
            )
            return {"success": False, "records_parsed": 0, "records_published": 0, "duplicates_skipped": 0}

        # Step 3: Parse JSON
        try:
            doc = json.loads(decompressed_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as json_err:
            retries = self._checkpoint_repo.record_file_failure(
                key, bucket, f"JSON decode error: {json_err}", etag, version_id
            )
            logger.error(
                f"Malformed JSON in s3://{bucket}/{key}: {json_err} "
                f"(attempt {retries}/{MAX_FILE_RETRIES})"
            )
            return {"success": False, "records_parsed": 0, "records_published": 0, "duplicates_skipped": 0}

        # Step 4: Extract and validate Records array
        records = doc.get("Records")
        if records is None:
            retries = self._checkpoint_repo.record_file_failure(
                key, bucket, "Missing 'Records' array in CloudTrail JSON", etag, version_id
            )
            logger.error(f"S3 file s3://{bucket}/{key} has no 'Records' field.")
            return {"success": False, "records_parsed": 0, "records_published": 0, "duplicates_skipped": 0}

        if not isinstance(records, list):
            retries = self._checkpoint_repo.record_file_failure(
                key, bucket, "'Records' field is not a list", etag, version_id
            )
            logger.error(f"S3 file s3://{bucket}/{key} 'Records' field is not a list.")
            return {"success": False, "records_parsed": 0, "records_published": 0, "duplicates_skipped": 0}

        parsed_count = len(records)

        # Empty records is a normal CloudTrail heartbeat file
        if parsed_count == 0:
            logger.info(f"S3 file s3://{bucket}/{key} contains 0 records (empty heartbeat).")
            self._checkpoint_repo.mark_file_processed(key, bucket, etag, 0, version_id)
            return {"success": True, "records_parsed": 0, "records_published": 0, "duplicates_skipped": 0}

        # Step 5 & 6: Prepare valid records and attach ingestion metadata
        records_to_publish = []
        duplicates_skipped = 0
        ingestion_ts = datetime.now(timezone.utc).isoformat()

        for idx, rec in enumerate(records):
            if not isinstance(rec, dict):
                logger.warning(
                    f"Record #{idx} in s3://{bucket}/{key} is not a dict. Skipping invalid record."
                )
                continue

            event_id = rec.get("eventID")
            # Step 7: Check individual eventID deduplication
            if event_id and self._checkpoint_repo.is_event_processed(event_id):
                duplicates_skipped += 1
                logger.debug(
                    f"Duplicate CloudTrail eventID '{event_id}' skipped in s3://{bucket}/{key}."
                )
                continue

            # Clone dict to attach metadata without mutating original source
            payload = dict(rec)
            payload["provider"] = "AWS"
            payload["s3_bucket"] = bucket
            payload["s3_key"] = key
            payload["s3_etag"] = etag
            payload["ingestion_source"] = "S3_CLOUDTRAIL"
            payload["ingestion_timestamp"] = ingestion_ts

            # Ensure region is populated from raw record or S3 regional key partition
            region_from_key = self._extract_region_from_key(key)
            if not payload.get("awsRegion") and region_from_key:
                payload["awsRegion"] = region_from_key
            if not payload.get("region"):
                payload["region"] = payload.get("awsRegion") or region_from_key

            records_to_publish.append(payload)

        if not records_to_publish and duplicates_skipped > 0:
            # All events in this file were already processed elsewhere
            logger.info(
                f"All {duplicates_skipped} event(s) in s3://{bucket}/{key} were already processed."
            )
            self._checkpoint_repo.mark_file_processed(
                key, bucket, etag, 0, version_id
            )
            return {
                "success": True,
                "records_parsed": parsed_count,
                "records_published": 0,
                "duplicates_skipped": duplicates_skipped,
            }

        # Step 8: Publish to Kafka with delivery confirmation
        pub_result = self._publish_records_to_kafka(records_to_publish, key)
        if not pub_result["success"]:
            retries = self._checkpoint_repo.record_file_failure(
                key, bucket, pub_result["error"], etag, version_id
            )
            logger.error(
                f"Kafka delivery failed for s3://{bucket}/{key}: {pub_result['error']} "
                f"(attempt {retries}/{MAX_FILE_RETRIES}). File NOT marked as processed."
            )
            return {
                "success": False,
                "records_parsed": parsed_count,
                "records_published": 0,
                "duplicates_skipped": duplicates_skipped,
                "kafka_failures": 1,
            }

        # Step 9: Mark successfully processed records and file checkpoint
        for published_rec in records_to_publish:
            eid = published_rec.get("eventID")
            if eid:
                self._checkpoint_repo.mark_event_processed(eid, key)

        self._checkpoint_repo.mark_file_processed(
            key, bucket, etag, len(records_to_publish), version_id
        )

        logger.info(
            f"Successfully processed s3://{bucket}/{key}: "
            f"{len(records_to_publish)} record(s) published to Kafka, "
            f"{duplicates_skipped} duplicate(s) skipped."
        )

        return {
            "success": True,
            "records_parsed": parsed_count,
            "records_published": len(records_to_publish),
            "duplicates_skipped": duplicates_skipped,
        }

    # ------------------------------------------------------------------
    # Safe Decompression & Kafka Publishing Helpers
    # ------------------------------------------------------------------

    def _decompress_gzip_safely(self, compressed_data: bytes) -> bytes:
        """
        Safely decompress gzip bytes with protection against zip bombs.
        """
        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode="rb") as gz:
            decompressed = gz.read(MAX_UNCOMPRESSED_BYTES + 1)
            if len(decompressed) > MAX_UNCOMPRESSED_BYTES:
                raise ValueError(
                    f"Decompressed size exceeds maximum safety limit ({MAX_UNCOMPRESSED_BYTES} bytes)."
                )
            return decompressed

    def _publish_records_to_kafka(
        self,
        records: List[Dict[str, Any]],
        file_key: str,
    ) -> Dict[str, Any]:
        """
        Publish records to the Kafka topic with per-batch delivery confirmation.
        """
        delivery_errors: List[str] = []

        def _delivery_callback(err, msg):
            if err is not None:
                delivery_errors.append(str(err))
                logger.error(f"Kafka delivery error for record from '{file_key}': {err}")

        for rec in records:
            try:
                sanitized_log = redact_sensitive_data(rec)
                event_name = sanitized_log.get("eventName", "Unknown")
                aws_region = sanitized_log.get("awsRegion", "Unknown")
                logger.debug(
                    f"Publishing CloudTrail event '{event_name}' (region: {aws_region}) to Kafka."
                )

                kafka_producer.producer.produce(
                    topic=settings.KAFKA_TOPIC,
                    value=json.dumps(rec),
                    callback=_delivery_callback,
                )
            except Exception as produce_err:
                return {
                    "success": False,
                    "error": f"Kafka produce() exception: {produce_err}",
                }

        # Flush and wait for callbacks
        remaining = kafka_producer.producer.flush(timeout=10)
        if remaining > 0:
            return {
                "success": False,
                "error": f"Kafka flush() timed out with {remaining} message(s) unconfirmed.",
            }

        if delivery_errors:
            return {
                "success": False,
                "error": f"Kafka callbacks reported {len(delivery_errors)} delivery error(s).",
            }

        return {"success": True, "error": None}

    # ------------------------------------------------------------------
    # Boto3 Client Factory
    # ------------------------------------------------------------------

    def _create_s3_client(self):
        """
        Create a boto3 S3 client using boto3.Session.

        Credential Precedence Order:
        1. Named AWS CLI profile: CLOUDTRAIL_S3_AWS_PROFILE (e.g. 'cloudguardian-s3')
        2. Dedicated S3 IAM credentials: CLOUDTRAIL_S3_ACCESS_KEY_ID / SECRET_ACCESS_KEY
        3. Shared AWS IAM credentials: AWS_ACCESS_KEY_ID / SECRET_ACCESS_KEY
        4. Standard AWS credential provider chain (IAM role, environment variables, default profile)
        """
        region = settings.CLOUDTRAIL_S3_REGION or settings.AWS_REGION
        session_kwargs = {"region_name": region}

        if settings.CLOUDTRAIL_S3_AWS_PROFILE:
            session_kwargs["profile_name"] = settings.CLOUDTRAIL_S3_AWS_PROFILE
        elif settings.CLOUDTRAIL_S3_ACCESS_KEY_ID and settings.CLOUDTRAIL_S3_SECRET_ACCESS_KEY:
            session_kwargs["aws_access_key_id"] = settings.CLOUDTRAIL_S3_ACCESS_KEY_ID
            session_kwargs["aws_secret_access_key"] = settings.CLOUDTRAIL_S3_SECRET_ACCESS_KEY
        elif settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        try:
            session = boto3.Session(**session_kwargs)
            return session.client("s3")
        except Exception as e:
            logger.error(f"Failed to create boto3 S3 client: {e}")
            return None


# Module-level singleton
s3_ingestion_service = CloudTrailS3IngestionService()
