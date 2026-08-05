from datetime import datetime, timezone
import uuid

from app.logger import logger
from app.storage.opensearch_client import client


class IOCRepository:

    INDEX_NAME = "ioc_database"

    def __init__(self):

        if not client.indices.exists(index=self.INDEX_NAME):

            mapping = {
                "mappings": {
                    "properties": {
                        "ioc_id": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "value": {"type": "keyword"},
                        "severity": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "description": {"type": "text"},
                        "enabled": {"type": "boolean"},
                        "created_at": {"type": "date"}
                    }
                }
            }

            client.indices.create(
                index=self.INDEX_NAME,
                body=mapping
            )

            logger.info(
                f"Created IOC index: {self.INDEX_NAME}"
            )

    # -----------------------------------
    # Create IOC
    # -----------------------------------
    def create_ioc(self, ioc: dict):

        ioc["ioc_id"] = f"IOC-{uuid.uuid4().hex[:8].upper()}"

        ioc["created_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        client.index(
            index=self.INDEX_NAME,
            id=ioc["ioc_id"],
            body=ioc,
            refresh=True
        )

        return ioc

    # -----------------------------------
    # Get IOC
    # -----------------------------------
    def get_ioc(self, ioc_id: str):

        try:

            response = client.get(
                index=self.INDEX_NAME,
                id=ioc_id
            )

            return response["_source"]

        except Exception:

            return None

    # -----------------------------------
    # Get All IOCs
    # -----------------------------------
    def get_all_iocs(self):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "query": {
                    "match_all": {}
                },
                "size": 1000
            }
        )

        return [
            hit["_source"]
            for hit in response["hits"]["hits"]
        ]

    # -----------------------------------
    # Delete IOC
    # -----------------------------------
    def delete_ioc(self, ioc_id: str):

        try:

            client.delete(
                index=self.INDEX_NAME,
                id=ioc_id,
                refresh=True
            )

            return True

        except Exception:

            return False

    # -----------------------------------
    # Update IOC
    # -----------------------------------
    def update_ioc(
        self,
        ioc_id: str,
        updates: dict
    ):

        client.update(
            index=self.INDEX_NAME,
            id=ioc_id,
            body={
                "doc": updates
            },
            refresh=True
        )

        return self.get_ioc(ioc_id)

    # -----------------------------------
    # Search IOC
    # -----------------------------------
    def search_value(
        self,
        value: str
    ):

        response = client.search(
            index=self.INDEX_NAME,
            body={
                "query": {
                    "term": {
                        "value.keyword": value
                    }
                }
            }
        )

        hits = response["hits"]["hits"]

        if not hits:
            return None

        return hits[0]["_source"]


ioc_repository = IOCRepository()