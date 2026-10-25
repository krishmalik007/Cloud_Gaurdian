import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.logger import logger
from app.storage.opensearch_client import client

DISK_CHECKPOINT_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "s3_checkpoints.json"


class S3CheckpointRepository:
    """
    Persistent checkpoint repository for S3 CloudTrail log ingestion.

    Tracks processed S3 files (object key, ETag, version, status, record counts)
    and individual CloudTrail eventID values to ensure restart safety, prevent
    duplicate ingestion, and provide at-least-once delivery with deduplication.

    Primary Store: OpenSearch indices `cloudguardian_s3_checkpoints` and
    `cloudguardian_processed_events`.
    Fallback / Resilience: Persistent disk file cache + thread-safe in-memory cache
    guaranteeing persistence across container restarts even when OpenSearch is
    temporarily unreachable.
    """

    CHECKPOINT_INDEX = "cloudguardian_s3_checkpoints"
    EVENT_INDEX = "cloudguardian_processed_events"

    def __init__(self, opensearch_client=None, disk_file: Optional[Path] = None):
        self.client = opensearch_client if opensearch_client is not None else client
        self._disk_file = disk_file or DISK_CHECKPOINT_FILE
        self._lock = threading.Lock()
        self._local_file_cache = {}
        self._local_event_cache = set()
        self._indices_initialized = False
        self._load_from_disk()
        self._init_indices()

    def _load_from_disk(self):
        """Load checkpoints from local persistent disk cache if present."""
        try:
            if self._disk_file.exists():
                with open(self._disk_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._local_file_cache = data.get("files", {})
                    self._local_event_cache = set(data.get("events", []))
                logger.info(
                    f"Loaded {len(self._local_file_cache)} file checkpoint(s) and "
                    f"{len(self._local_event_cache)} event checkpoint(s) from persistent disk cache: {self._disk_file}"
                )
        except Exception as e:
            logger.warning(f"Could not load S3 checkpoints from disk: {e}")

    def _flush_to_disk(self):
        """Flush in-memory checkpoints atomically to local persistent disk file."""
        try:
            self._disk_file.parent.mkdir(parents=True, exist_ok=True)
            tmp_file = self._disk_file.with_suffix(".tmp")
            data = {
                "files": self._local_file_cache,
                "events": list(self._local_event_cache),
            }
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            tmp_file.replace(self._disk_file)
        except Exception as e:
            logger.debug(f"Could not flush S3 checkpoints to disk: {e}")

    def _init_indices(self):
        """Create the OpenSearch indices if they do not exist."""
        try:
            if not self.client.indices.exists(index=self.CHECKPOINT_INDEX):
                checkpoint_mapping = {
                    "mappings": {
                        "properties": {
                            "file_key": {"type": "keyword"},
                            "bucket": {"type": "keyword"},
                            "etag": {"type": "keyword"},
                            "version_id": {"type": "keyword"},
                            "status": {"type": "keyword"},
                            "records_count": {"type": "long"},
                            "retry_count": {"type": "long"},
                            "error_message": {"type": "text"},
                            "last_attempt_at": {"type": "date"},
                            "processed_at": {"type": "date"},
                        }
                    }
                }
                self.client.indices.create(
                    index=self.CHECKPOINT_INDEX,
                    body=checkpoint_mapping
                )
                logger.info(f"Created OpenSearch index: {self.CHECKPOINT_INDEX}")

            if not self.client.indices.exists(index=self.EVENT_INDEX):
                event_mapping = {
                    "mappings": {
                        "properties": {
                            "event_id": {"type": "keyword"},
                            "file_key": {"type": "keyword"},
                            "processed_at": {"type": "date"},
                        }
                    }
                }
                self.client.indices.create(
                    index=self.EVENT_INDEX,
                    body=event_mapping
                )
                logger.info(f"Created OpenSearch index: {self.EVENT_INDEX}")

            self._indices_initialized = True
        except Exception as e:
            logger.warning(
                f"OpenSearch indices check/creation failed for S3 checkpoints: {e}. "
                "Operating with in-memory resilient fallback."
            )
            self._indices_initialized = False

    @staticmethod
    def _doc_id(key: str) -> str:
        """Generate a SHA-256 document ID for an S3 object key."""
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def is_file_processed(self, file_key: str, etag: Optional[str] = None) -> bool:
        """
        Check if an S3 object has already been fully processed.
        Returns True if status is 'PROCESSED'.
        """
        doc_id = self._doc_id(file_key)

        # 1. Check local cache first
        with self._lock:
            local_record = self._local_file_cache.get(doc_id)
            if local_record and local_record.get("status") == "PROCESSED":
                if etag is None or local_record.get("etag") == etag:
                    return True

        # 2. Check OpenSearch
        try:
            response = self.client.get(index=self.CHECKPOINT_INDEX, id=doc_id)
            if isinstance(response, dict):
                source = response.get("_source", {})
                if isinstance(source, dict) and source.get("status") == "PROCESSED":
                    if etag is None or source.get("etag") == etag:
                        with self._lock:
                            self._local_file_cache[doc_id] = source
                        return True
        except Exception:
            pass

        return False

    def get_retry_count(self, file_key: str) -> int:
        """Get the current retry count for a failed file."""
        doc_id = self._doc_id(file_key)
        with self._lock:
            if doc_id in self._local_file_cache:
                return self._local_file_cache[doc_id].get("retry_count", 0)

        try:
            response = self.client.get(index=self.CHECKPOINT_INDEX, id=doc_id)
            if isinstance(response, dict):
                source = response.get("_source", {})
                if isinstance(source, dict):
                    return int(source.get("retry_count", 0))
        except Exception:
            pass
        return 0

    def mark_file_processed(
        self,
        file_key: str,
        bucket: str,
        etag: Optional[str] = None,
        records_count: int = 0,
        version_id: Optional[str] = None,
    ) -> None:
        """Mark an S3 object as fully processed."""
        doc_id = self._doc_id(file_key)
        now_iso = datetime.now(timezone.utc).isoformat()
        doc = {
            "file_key": file_key,
            "bucket": bucket,
            "etag": etag or "",
            "version_id": version_id or "",
            "status": "PROCESSED",
            "records_count": records_count,
            "retry_count": 0,
            "error_message": "",
            "last_attempt_at": now_iso,
            "processed_at": now_iso,
        }

        with self._lock:
            self._local_file_cache[doc_id] = doc
            self._flush_to_disk()

        try:
            self.client.index(
                index=self.CHECKPOINT_INDEX,
                id=doc_id,
                body=doc,
                refresh=True
            )
        except Exception as e:
            logger.debug(f"Failed to persist file checkpoint to OpenSearch: {e}")

    def record_file_failure(
        self,
        file_key: str,
        bucket: str,
        error_message: str,
        etag: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> int:
        """
        Record a failure for an S3 object and increment its retry count.
        Returns the updated retry count.
        """
        doc_id = self._doc_id(file_key)
        current_retries = self.get_retry_count(file_key)
        updated_retries = current_retries + 1
        now_iso = datetime.now(timezone.utc).isoformat()

        doc = {
            "file_key": file_key,
            "bucket": bucket,
            "etag": etag or "",
            "version_id": version_id or "",
            "status": "FAILED",
            "records_count": 0,
            "retry_count": updated_retries,
            "error_message": error_message[:1000],
            "last_attempt_at": now_iso,
        }

        with self._lock:
            self._local_file_cache[doc_id] = doc
            self._flush_to_disk()

        try:
            self.client.index(
                index=self.CHECKPOINT_INDEX,
                id=doc_id,
                body=doc,
                refresh=True
            )
        except Exception as e:
            logger.debug(f"Failed to record file failure in OpenSearch: {e}")

        return updated_retries

    def is_event_processed(self, event_id: str) -> bool:
        """Check if an individual CloudTrail eventID was already processed."""
        if not event_id:
            return False

        with self._lock:
            if event_id in self._local_event_cache:
                return True

        try:
            response = self.client.get(index=self.EVENT_INDEX, id=event_id)
            if isinstance(response, dict) and response.get("found") is True:
                with self._lock:
                    self._local_event_cache.add(event_id)
                    self._flush_to_disk()
                return True
        except Exception:
            pass

        return False

    def mark_event_processed(self, event_id: str, file_key: str = "") -> None:
        """Record an individual CloudTrail eventID as processed."""
        if not event_id:
            return

        with self._lock:
            self._local_event_cache.add(event_id)
            self._flush_to_disk()

        try:
            doc = {
                "event_id": event_id,
                "file_key": file_key,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }
            self.client.index(
                index=self.EVENT_INDEX,
                id=event_id,
                body=doc,
                refresh=False  # Do not force immediate refresh on every event for throughput
            )
        except Exception:
            pass

    def clear_local_cache(self, remove_disk: bool = True) -> None:
        """Clear local in-memory caches and optionally persistent disk cache (primarily for unit tests)."""
        with self._lock:
            self._local_file_cache.clear()
            self._local_event_cache.clear()
            if remove_disk and self._disk_file.exists():
                try:
                    self._disk_file.unlink()
                except Exception:
                    pass


s3_checkpoint_repository = S3CheckpointRepository()
