from app.storage.opensearch_client import client


class IncidentRepository:

    INDEX_NAME = "incidents"

    def __init__(self):

        if not client.indices.exists(index=self.INDEX_NAME):
            client.indices.create(index=self.INDEX_NAME)

    def save_incident(self, incident):

        response = client.index(
            index=self.INDEX_NAME,
            id=incident["incident_id"],
            body=incident,
            refresh=True
        )

        return response

    def get_incident(self, incident_id):

        return client.get(
            index=self.INDEX_NAME,
            id=incident_id
        )

    def get_all_incidents(self):

        return client.search(
            index=self.INDEX_NAME,
            body={
                "query": {
                    "match_all": {}
                }
            }
        )

    def delete_incident(self, incident_id):

        return client.delete(
            index=self.INDEX_NAME,
            id=incident_id,
            refresh=True
        )


incident_repository = IncidentRepository()