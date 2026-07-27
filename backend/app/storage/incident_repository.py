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


incident_repository = IncidentRepository()