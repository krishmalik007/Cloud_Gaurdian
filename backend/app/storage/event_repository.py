import hashlib
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.logger import logger
from app.storage.opensearch_client import client
from app.utils.redaction import redact_sensitive_data


_USE_GLOBAL = object()


class EventRepository:
    """
    Persistent repository for raw and normalized cloud events in OpenSearch.

    Index: `events`
    Ensures every ingested event (including zero-risk routine AWS API events)
    is stored and searchable without requiring a security incident to be created.
    Uses the CloudTrail eventID as document ID for idempotent writes.
    """

    INDEX_NAME = "events"

    def __init__(self, opensearch_client=_USE_GLOBAL):
        self._opensearch_client = opensearch_client
        self._lock = threading.Lock()
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._init_index()

    @property
    def client(self):
        if self._opensearch_client is not _USE_GLOBAL:
            return self._opensearch_client
        import app.storage.opensearch_client as os_mod
        return os_mod.client

    @client.setter
    def client(self, value):
        self._opensearch_client = value

    @client.deleter
    def client(self):
        self._opensearch_client = _USE_GLOBAL

    def _init_index(self):
        """Initialize the OpenSearch events index if it does not exist."""
        try:
            if not self.client.indices.exists(index=self.INDEX_NAME):
                mapping = {
                    "mappings": {
                        "properties": {
                            "event_id": {"type": "keyword"},
                            "event_name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "event_type": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "provider": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "username": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "region": {"type": "keyword"},
                            "source_ip": {"type": "keyword"},
                            "timestamp": {"type": "date"},
                            "risk_score": {"type": "long"},
                            "risk_level": {"type": "keyword"},
                            "priority": {"type": "keyword"},
                            "status": {"type": "keyword"},
                            "analyst_attention": {"type": "keyword"},
                            "threat_score": {"type": "long"},
                            "threat_level": {"type": "keyword"},
                            "threat_tags": {"type": "keyword"},
                            "alerts": {"type": "object"},
                            "raw_log": {"type": "object"},
                            "is_incident": {"type": "boolean"},
                            "incident_id": {"type": "keyword"},
                            "event_category": {"type": "keyword"},
                            "ingested_at": {"type": "date"},
                        }
                    }
                }
                self.client.indices.create(index=self.INDEX_NAME, body=mapping)
                logger.info(f"Created OpenSearch index: {self.INDEX_NAME}")
        except Exception as e:
            logger.warning(
                f"OpenSearch index check/creation failed for events: {e}. "
                "Operating with in-memory resilient fallback."
            )

    @staticmethod
    def _doc_id(event_data: dict) -> str:
        """Derive a stable document ID using event_id or fallback safely."""
        eid = event_data.get("event_id") or event_data.get("eventID")
        if eid:
            return str(eid)
        raw = event_data.get("raw_log")
        if isinstance(raw, dict):
            req_id = raw.get("requestID") or raw.get("requestId")
            if req_id:
                return f"req-{req_id}"
        # When eventID and requestID are missing, generate a unique random ID
        # to ensure unrelated events are not incorrectly deduplicated
        return f"evt-{uuid.uuid4().hex}"

    def save_event(self, event_data: dict) -> dict:
        """
        Store and index an event in OpenSearch using idempotent document ID.
        Applies data redaction to raw_log before persistence.
        """
        doc_id = self._doc_id(event_data)
        event_copy = dict(event_data)
        event_copy["event_id"] = doc_id

        if "raw_log" in event_copy and event_copy["raw_log"]:
            event_copy["raw_log"] = redact_sensitive_data(event_copy["raw_log"])

        if "ingested_at" not in event_copy:
            event_copy["ingested_at"] = datetime.now(timezone.utc).isoformat()

        # Defensive enrichment: ensure top-level searchable fields are never null
        summary = event_copy.get("event_summary") if isinstance(event_copy.get("event_summary"), dict) else {}
        raw = event_copy.get("raw_log") if isinstance(event_copy.get("raw_log"), dict) else {}

        if not event_copy.get("region") or str(event_copy.get("region")).lower() in {"none", "null"}:
            raw_detail = raw.get("detail") if isinstance(raw.get("detail"), dict) else {}
            event_copy["region"] = (
                event_copy.get("awsRegion")
                or event_copy.get("aws_region")
                or summary.get("region")
                or raw.get("awsRegion")
                or raw.get("aws_region")
                or raw.get("region")
                or raw_detail.get("awsRegion")
                or raw_detail.get("aws_region")
                or raw_detail.get("region")
                or raw.get("eventbridge_region")
                or "Unknown"
            )

        if not event_copy.get("source_ip") or event_copy.get("source_ip") == "None":
            event_copy["source_ip"] = (
                summary.get("source_ip")
                or raw.get("sourceIPAddress")
                or raw.get("source_ip")
                or "-"
            )

        if not event_copy.get("event_name") or event_copy.get("event_name") == "None":
            event_copy["event_name"] = (
                summary.get("event_name")
                or raw.get("eventName")
                or raw.get("event_name")
                or "Unknown"
            )

        if not event_copy.get("timestamp") or event_copy.get("timestamp") == "None":
            raw_ts = (
                summary.get("timestamp")
                or raw.get("eventTime")
                or raw.get("event_time")
                or event_copy.get("event_time")
                or event_copy.get("ingested_at")
            )
            event_copy["timestamp"] = (
                raw_ts.isoformat() if isinstance(raw_ts, datetime) else str(raw_ts or datetime.now(timezone.utc).isoformat())
            )

        with self._lock:
            self._local_cache[doc_id] = event_copy

        try:
            self.client.index(
                index=self.INDEX_NAME,
                id=doc_id,
                body=event_copy,
                refresh=True
            )
        except Exception as e:
            logger.debug(f"Failed to index event {doc_id} to OpenSearch: {e}")

        return event_copy

    def get_event(self, event_id: str) -> Optional[dict]:
        """Retrieve an event by its ID."""
        if not event_id:
            return None

        with self._lock:
            if event_id in self._local_cache:
                return self._local_cache[event_id]

        try:
            response = self.client.get(index=self.INDEX_NAME, id=event_id)
            if isinstance(response, dict):
                source = response.get("_source")
                if source:
                    with self._lock:
                        self._local_cache[event_id] = source
                    return source
        except Exception:
            pass

        return None

    def search_events(
        self,
        provider: Optional[str] = None,
        risk_level: Optional[str] = None,
        status: Optional[str] = None,
        username: Optional[str] = None,
        event_name: Optional[str] = None,
        event_type: Optional[str] = None,
        region: Optional[str] = None,
        is_incident: Optional[bool] = None,
        search: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> dict:
        """
        Search cloud events from the `events` OpenSearch index with filtering,
        pagination, deterministic sorting, and full-text search.
        """
        must = []

        if provider:
            if "," in provider:
                must.append({"terms": {"provider.keyword": [p.strip() for p in provider.split(",") if p.strip()]}})
            else:
                must.append({"term": {"provider.keyword": provider.strip()}})

        if risk_level:
            if "," in risk_level:
                must.append({"terms": {"risk_level": [r.strip().upper() for r in risk_level.split(",") if r.strip()]}})
            else:
                must.append({"term": {"risk_level": risk_level.strip().upper()}})

        if status:
            if "," in status:
                must.append({"terms": {"status": [s.strip().upper() for s in status.split(",") if s.strip()]}})
            else:
                must.append({"term": {"status": status.strip().upper()}})

        if username:
            must.append({"term": {"username.keyword": username.strip()}})

        if event_name:
            if "," in event_name:
                must.append({"terms": {"event_name.keyword": [e.strip() for e in event_name.split(",") if e.strip()]}})
            else:
                must.append({"term": {"event_name.keyword": event_name.strip()}})

        if event_type:
            if "," in event_type:
                must.append({"terms": {"event_type.keyword": [t.strip().upper() for t in event_type.split(",") if t.strip()]}})
            else:
                must.append({"term": {"event_type.keyword": event_type.strip().upper()}})

        if region:
            if "," in region:
                must.append({"terms": {"region": [r.strip() for r in region.split(",") if r.strip()]}})
            else:
                must.append({"term": {"region": region.strip()}})

        if is_incident is not None:
            must.append({"term": {"is_incident": is_incident}})

        if search:
            must.append({
                "multi_match": {
                    "query": search.strip(),
                    "fields": [
                        "event_name^3",
                        "event_name.keyword^3",
                        "username^2",
                        "username.keyword^2",
                        "source_ip",
                        "event_id",
                        "region",
                        "event_type"
                    ],
                    "type": "best_fields"
                }
            })

        if start_date or end_date:
            date_range = {}
            if start_date:
                date_range["gte"] = start_date
            if end_date:
                date_range["lte"] = end_date
            must.append({"range": {"timestamp": date_range}})

        sort_field_map = {
            "timestamp": "timestamp",
            "ingested_at": "ingested_at",
            "risk_score": "risk_score",
            "status": "status",
            "provider": "provider.keyword",
            "username": "username.keyword",
            "event_name": "event_name.keyword",
            "event_type": "event_type.keyword",
            "region": "region"
        }
        resolved_sort_field = sort_field_map.get(sort_by, "timestamp")

        # OpenSearch pagination window protection: from + size <= 10000
        safe_size = max(1, min(size, 500))
        safe_from = max(0, min((page - 1) * safe_size, 10000 - safe_size))

        query_body = {
            "from": safe_from,
            "size": safe_size,
            "sort": [
                {
                    resolved_sort_field: {
                        "order": sort_order if sort_order in ["asc", "desc"] else "desc",
                        "unmapped_type": "date" if "time" in resolved_sort_field or "at" in resolved_sort_field else "keyword"
                    }
                },
                {
                    "event_id": {
                        "order": "desc",
                        "unmapped_type": "keyword"
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": must if must else [{"match_all": {}}]
                }
            }
        }

        try:
            response = self.client.search(
                index=self.INDEX_NAME,
                body=query_body
            )

            total = response["hits"]["total"]["value"]
            events = [hit["_source"] for hit in response["hits"]["hits"]]

            return {
                "page": page,
                "size": size,
                "total": total,
                "events": events
            }
        except Exception as e:
            logger.error(f"Event search failed in OpenSearch: {e}")
            with self._lock:
                all_cached = list(self._local_cache.values())
                filtered = all_cached
                if provider:
                    filtered = [e for e in filtered if e.get("provider") == provider]
                if risk_level:
                    allowed_risks = [r.strip().upper() for r in risk_level.split(",")]
                    filtered = [e for e in filtered if str(e.get("risk_level", "")).upper() in allowed_risks]
                if status:
                    allowed_statuses = [s.strip().upper() for s in status.split(",")]
                    filtered = [e for e in filtered if str(e.get("status", "")).upper() in allowed_statuses]
                if region:
                    allowed_regions = [r.strip() for r in region.split(",")]
                    filtered = [e for e in filtered if e.get("region") in allowed_regions]
                if event_name:
                    allowed_events = [ev.strip() for ev in event_name.split(",")]
                    filtered = [e for e in filtered if e.get("event_name") in allowed_events]
                if event_type:
                    allowed_types = [t.strip().upper() for t in event_type.split(",")]
                    filtered = [e for e in filtered if str(e.get("event_type", "")).upper() in allowed_types]
                if is_incident is not None:
                    filtered = [e for e in filtered if e.get("is_incident") == is_incident]
                if search:
                    s_lower = search.strip().lower()
                    filtered = [
                        e for e in filtered
                        if s_lower in str(e.get("event_name", "")).lower()
                        or s_lower in str(e.get("username", "")).lower()
                        or s_lower in str(e.get("source_ip", "")).lower()
                        or s_lower in str(e.get("event_id", "")).lower()
                    ]
                total = len(filtered)
                start_idx = (page - 1) * size
                return {
                    "page": page,
                    "size": size,
                    "total": total,
                    "events": filtered[start_idx:start_idx + size]
                }

    def count_events(self) -> int:
        """Return total number of documents in the events index."""
        try:
            res = self.client.count(index=self.INDEX_NAME)
            return res.get("count", 0)
        except Exception as e:
            logger.debug(f"Failed to count events in OpenSearch: {e}")
            with self._lock:
                return len(self._local_cache)

    def get_event_stats(self) -> dict:
        """Retrieve aggregated event distribution metrics."""
        try:
            response = self.client.search(
                index=self.INDEX_NAME,
                body={
                    "size": 0,
                    "aggs": {
                        "providers": {"terms": {"field": "provider.keyword"}},
                        "categories": {"terms": {"field": "status"}},
                        "is_incident": {"terms": {"field": "is_incident"}},
                        "risk_levels": {"terms": {"field": "risk_level"}}
                    }
                }
            )
            total = response["hits"]["total"]["value"]
            providers = [
                {"provider": b["key"], "count": b["doc_count"]}
                for b in response.get("aggregations", {}).get("providers", {}).get("buckets", [])
            ]
            statuses = [
                {"status": b["key"], "count": b["doc_count"]}
                for b in response.get("aggregations", {}).get("categories", {}).get("buckets", [])
            ]
            risks = [
                {"risk_level": b["key"], "count": b["doc_count"]}
                for b in response.get("aggregations", {}).get("risk_levels", {}).get("buckets", [])
            ]
            incident_count = 0
            for b in response.get("aggregations", {}).get("is_incident", {}).get("buckets", []):
                if b["key"] == 1 or b["key"] is True or str(b.get("key_as_string", "")).lower() == "true":
                    incident_count = b["doc_count"]

            return {
                "total_events": total,
                "incident_events": incident_count,
                "informational_events": max(0, total - incident_count),
                "providers": providers,
                "statuses": statuses,
                "risk_levels": risks
            }
        except Exception as e:
            logger.debug(f"Failed to get event stats: {e}")
            total = self.count_events()
            return {
                "total_events": total,
                "incident_events": 0,
                "informational_events": total,
                "providers": [],
                "statuses": [],
                "risk_levels": []
            }

    def get_all_events(self, limit: int = 100) -> list:
        """Retrieve recent events from the events index."""
        result = self.search_events(page=1, size=limit)
        return result.get("events", [])

    def is_event_stored(self, event_id: str) -> bool:
        """Check if an event is already stored in the events repository."""
        return self.get_event(event_id) is not None

    def clear_local_cache(self) -> None:
        """Clear local in-memory cache (primarily for unit tests)."""
        with self._lock:
            self._local_cache.clear()


event_repository = EventRepository()
