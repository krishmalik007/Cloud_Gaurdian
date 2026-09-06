from opensearchpy import OpenSearch
from app.storage.opensearch_client import client as shared_client
from app.config import get_settings
from app.logger import logger

settings = get_settings()


class OpenSearchService:
    """
    Handles all interactions with the OpenSearch cluster.
    """

    def __init__(self):
        self.client = shared_client

    def ping(self) -> bool:
        """
        Check if OpenSearch is reachable.
        """
        try:
            if self.client.ping():
                logger.info("Connected to OpenSearch successfully.")
                return True

            logger.error("Unable to connect to OpenSearch.")
            return False

        except Exception as e:
            logger.error(f"OpenSearch Connection Error: {e}")
            return False


opensearch_service = OpenSearchService()