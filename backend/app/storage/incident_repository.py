import threading

from app.logger import logger
from app.storage.opensearch_client import client
from app.utils.redaction import redact_sensitive_data


_USE_GLOBAL = object()


class IncidentRepository:

    INDEX_NAME = "incidents"

    def __init__(self, opensearch_client=_USE_GLOBAL):
        self._opensearch_client = opensearch_client
        self._lock = threading.Lock()
        self._local_cache = {}
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
        try:
            if not self.client.indices.exists(index=self.INDEX_NAME):
                mapping = {
                    "mappings": {
                        "properties": {
                            "incident_id": {"type": "keyword"},
                            "status": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "priority": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "risk_score": {"type": "long"},
                            "risk_level": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "username": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "provider": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"},
                            "alerts": {"type": "object"},
                            "event_summary": {"type": "object"},
                            "raw_log": {"type": "object"},
                            "notes": {"type": "object"},
                            "analyst_attention": {"type": "keyword"},
                            "xdr_assessment": {"type": "text"}
                        }
                    }
                }
                self.client.indices.create(index=self.INDEX_NAME, body=mapping)
                logger.info(f"Created OpenSearch index: {self.INDEX_NAME}")
        except Exception as e:
            logger.debug(f"OpenSearch index check failed in IncidentRepository: {e}")

    def save_incident(self, incident: dict):
        # Defense in depth: Ensure any raw logs are fully redacted before storage
        if "raw_log" in incident:
            incident["raw_log"] = redact_sensitive_data(incident["raw_log"])

        summary = incident.get("event_summary") if isinstance(incident.get("event_summary"), dict) else {}
        raw = incident.get("raw_log") if isinstance(incident.get("raw_log"), dict) else {}

        if not incident.get("region") or incident.get("region") == "None":
            incident["region"] = (
                summary.get("region")
                or raw.get("awsRegion")
                or raw.get("region")
                or "Unknown"
            )

        if not incident.get("source_ip") or incident.get("source_ip") == "None":
            incident["source_ip"] = (
                summary.get("source_ip")
                or raw.get("sourceIPAddress")
                or raw.get("source_ip")
                or "-"
            )

        if not incident.get("event_name") or incident.get("event_name") == "None":
            incident["event_name"] = (
                summary.get("event_name")
                or raw.get("eventName")
                or raw.get("event_name")
                or "Unknown"
            )

        with self._lock:
            self._local_cache[incident["incident_id"]] = incident

        self.client.index(
            index=self.INDEX_NAME,
            id=incident["incident_id"],
            body=incident,
            refresh=True
        )

        return incident

    def get_incident(self, incident_id: str):
        with self._lock:
            if incident_id in self._local_cache:
                return self._local_cache[incident_id]

        try:
            response = self.client.get(
                index=self.INDEX_NAME,
                id=incident_id
            )

            if isinstance(response, dict):
                source = response.get("_source")
                if source:
                    with self._lock:
                        self._local_cache[incident_id] = source
                    return source

        except Exception:
            pass

        return None

    def get_all_incidents(self):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {
                        "created_at": {
                            "order": "desc"
                        }
                    }
                ]
            }
        )

        incidents = []

        for hit in response["hits"]["hits"]:
            incidents.append(hit["_source"])

        return incidents

    def delete_incident(self, incident_id: str):
        with self._lock:
            self._local_cache.pop(incident_id, None)
        try:
            client.delete(
                index=self.INDEX_NAME,
                id=incident_id,
                refresh=True
            )

            return True

        except Exception:
            return False

    def clear_local_cache(self):
        """Clear local cache (primarily for unit tests)."""
        with self._lock:
            self._local_cache.clear()

    # --------------------------------------------------------
    # Dashboard APIs
    # --------------------------------------------------------

    def get_dashboard_summary(self):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "size": 0,
                "aggs": {
                    "status": {
                        "terms": {
                            "field": "status.keyword"
                        }
                    },
                    "risk": {
                        "terms": {
                            "field": "risk_level.keyword"
                        }
                    }
                }
            }
        )

        total = response["hits"]["total"]["value"]

        open_count = 0
        investigating_count = 0
        resolved_count = 0

        for bucket in response["aggregations"]["status"]["buckets"]:
            if bucket["key"] == "OPEN":
                open_count = bucket["doc_count"]
            elif bucket["key"] == "INVESTIGATING":
                investigating_count = bucket["doc_count"]
            elif bucket["key"] == "RESOLVED":
                resolved_count = bucket["doc_count"]

        high = medium = low = 0

        for bucket in response["aggregations"]["risk"]["buckets"]:
            if bucket["key"] == "HIGH":
                high = bucket["doc_count"]
            elif bucket["key"] == "MEDIUM":
                medium = bucket["doc_count"]
            elif bucket["key"] == "LOW":
                low = bucket["doc_count"]

        total_events = 0
        try:
            from app.storage.event_repository import event_repository
            total_events = event_repository.count_events()
        except Exception:
            pass

        return {
            "total_incidents": total,
            "total_events": total_events,
            "open_incidents": open_count,
            "investigating_incidents": investigating_count,
            "resolved_incidents": resolved_count,
            "high_risk": high,
            "medium_risk": medium,
            "low_risk": low
        }

    def get_provider_stats(self):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "size": 0,
                "aggs": {
                    "providers": {
                        "terms": {
                            "field": "provider.keyword"
                        }
                    }
                }
            }
        )

        providers = []

        for bucket in response["aggregations"]["providers"]["buckets"]:
            providers.append({
                "provider": bucket["key"],
                "count": bucket["doc_count"]
            })

        return providers

    def get_risk_distribution(self):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "size": 0,
                "aggs": {
                    "risk": {
                        "terms": {
                            "field": "risk_level.keyword"
                        }
                    }
                }
            }
        )

        risks = []

        for bucket in response["aggregations"]["risk"]["buckets"]:
            risks.append({
                "risk_level": bucket["key"],
                "count": bucket["doc_count"]
            })

        return risks

    def get_recent_incidents(self, limit: int = 10):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "size": limit,
                "sort": [
                    {
                        "created_at": {
                            "order": "desc"
                        }
                    }
                ]
            }
        )

        incidents = []

        for hit in response["hits"]["hits"]:
            incidents.append(hit["_source"])

        return incidents

    # --------------------------------------------------------
    # Search API
    # --------------------------------------------------------

    def search_incidents(
        self,
        provider=None,
        risk_level=None,
        status=None,
        username=None,
        page=1,
        size=10,
        sort_by="created_at",
        sort_order="desc"
    ):

        must = []

        if provider:
            must.append({
                "term": {
                    "provider.keyword": provider
                }
            })

        if risk_level:
            if "," in risk_level:
                must.append({
                    "terms": {
                        "risk_level.keyword": risk_level.split(",")
                    }
                })
            else:
                must.append({
                    "term": {
                        "risk_level.keyword": risk_level
                    }
                })

        if status:
            if "," in status:
                must.append({
                    "terms": {
                        "status.keyword": status.split(",")
                    }
                })
            else:
                must.append({
                    "term": {
                        "status.keyword": status
                    }
                })

        if username:
            must.append({
                "term": {
                    "username.keyword": username
                }
            })

        sort_field = sort_by if sort_by in ["created_at", "risk_score", "status", "priority", "risk_level"] else "created_at"
        safe_size = max(1, min(size, 500))
        safe_from = max(0, min((page - 1) * safe_size, 10000 - safe_size))

        query = {
            "from": safe_from,
            "size": safe_size,
            "sort": [
                {
                    sort_field: {
                        "order": sort_order if sort_order in ["asc", "desc"] else "desc",
                        "unmapped_type": "date" if "created_at" in sort_field else "keyword"
                    }
                },
                {
                    "incident_id.keyword": {
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
                body=query
            )
            total = response["hits"]["total"]["value"]
            incidents = [hit["_source"] for hit in response["hits"]["hits"]]
            return {
                "page": page,
                "size": size,
                "total": total,
                "incidents": incidents
            }
        except Exception as e:
            logger.error(f"Search incidents failed in OpenSearch: {e}")
            with self._lock:
                all_cached = list(self._local_cache.values())
                filtered = all_cached
                if provider:
                    filtered = [i for i in filtered if i.get("provider") == provider]
                if risk_level:
                    allowed_risks = [r.strip().upper() for r in risk_level.split(",")]
                    filtered = [i for i in filtered if str(i.get("risk_level", "")).upper() in allowed_risks]
                if status:
                    allowed_statuses = [s.strip().upper() for s in status.split(",")]
                    filtered = [i for i in filtered if str(i.get("status", "")).upper() in allowed_statuses]
                if username:
                    filtered = [i for i in filtered if i.get("username") == username]
                total = len(filtered)
                start_idx = (page - 1) * size
                return {
                    "page": page,
                    "size": size,
                    "total": total,
                    "incidents": filtered[start_idx:start_idx + size]
                }


incident_repository = IncidentRepository()