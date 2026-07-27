from typing import Optional

from app.storage.opensearch_client import client


class AuditRepository:
    INDEX_NAME = "audit_logs"

    def __init__(self):
        self.client = client
        self._create_index()

    def _create_index(self):
        """
        Create audit_logs index if it does not exist.
        """

        if not self.client.indices.exists(index=self.INDEX_NAME):

            mapping = {
                "mappings": {
                    "properties": {
                        "audit_id": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "username": {"type": "keyword"},
                        "action": {"type": "keyword"},
                        "resource": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "ip_address": {"type": "ip"},
                        "timestamp": {"type": "date"}
                    }
                }
            }

            self.client.indices.create(
                index=self.INDEX_NAME,
                body=mapping
            )

    def create_log(self, audit_log: dict):
        """
        Store an audit log.
        """

        self.client.index(
            index=self.INDEX_NAME,
            id=audit_log["audit_id"],
            body=audit_log,
            refresh=True
        )

    def get_all_logs(self):
        """
        Retrieve all audit logs.
        """

        result = self.client.search(
            index=self.INDEX_NAME,
            body={
                "query": {
                    "match_all": {}
                },
                "sort": [
                    {
                        "timestamp": {
                            "order": "desc"
                        }
                    }
                ],
                "size": 1000
            }
        )

        return [
            hit["_source"]
            for hit in result["hits"]["hits"]
        ]

    def get_log(self, audit_id: str) -> Optional[dict]:
        """
        Retrieve a single audit log.
        """

        try:
            result = self.client.get(
                index=self.INDEX_NAME,
                id=audit_id
            )

            return result["_source"]

        except Exception:
            return None
        