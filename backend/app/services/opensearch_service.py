from opensearchpy import OpenSearch
from app.config import get_settings
from app.logger import logger

settings = get_settings()


class OpenSearchService:
    """
    Handles all interactions with the OpenSearch cluster.
    """

    def __init__(self):
        self.client = OpenSearch(
            hosts=[
                {
                    "host": settings.OPENSEARCH_HOST,
                    "port": settings.OPENSEARCH_PORT,
                }
            ],
            http_auth=(
                settings.OPENSEARCH_USERNAME,
                settings.OPENSEARCH_PASSWORD,
            ),
            use_ssl=settings.OPENSEARCH_USE_SSL,
            verify_certs=False,
        )

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