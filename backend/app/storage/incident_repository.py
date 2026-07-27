from app.logger import logger
from app.storage.opensearch_client import client


class IncidentRepository:

    INDEX_NAME = "incidents"

    def __init__(self):
        if not client.indices.exists(index=self.INDEX_NAME):
            client.indices.create(index=self.INDEX_NAME)
            logger.info(f"Created OpenSearch index: {self.INDEX_NAME}")

    def save_incident(self, incident: dict):
        client.index(
            index=self.INDEX_NAME,
            id=incident["incident_id"],
            body=incident,
            refresh=True
        )

        return incident

    def get_incident(self, incident_id: str):
        try:
            response = client.get(
                index=self.INDEX_NAME,
                id=incident_id
            )

            return response["_source"]

        except Exception:
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
        try:
            client.delete(
                index=self.INDEX_NAME,
                id=incident_id,
                refresh=True
            )

            return True

        except Exception:
            return False

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
        closed_count = 0

        for bucket in response["aggregations"]["status"]["buckets"]:
            if bucket["key"] == "OPEN":
                open_count = bucket["doc_count"]
            elif bucket["key"] == "CLOSED":
                closed_count = bucket["doc_count"]

        high = medium = low = 0

        for bucket in response["aggregations"]["risk"]["buckets"]:
            if bucket["key"] == "HIGH":
                high = bucket["doc_count"]
            elif bucket["key"] == "MEDIUM":
                medium = bucket["doc_count"]
            elif bucket["key"] == "LOW":
                low = bucket["doc_count"]

        return {
            "total_incidents": total,
            "open_incidents": open_count,
            "closed_incidents": closed_count,
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
            must.append({
                "term": {
                    "risk_level.keyword": risk_level
                }
            })

        if status:
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

        query = {
            "from": (page - 1) * size,
            "size": size,
            "sort": [
                {
                    sort_by: {
                        "order": sort_order
                    }
                }
            ],
            "query": {
                "bool": {
                    "must": must
                }
            }
        }

        response = client.search(
            index=self.INDEX_NAME,
            body=query
        )

        incidents = []

        for hit in response["hits"]["hits"]:
            incidents.append(hit["_source"])

        return {
            "page": page,
            "size": size,
            "total": response["hits"]["total"]["value"],
            "incidents": incidents
        }


incident_repository = IncidentRepository()