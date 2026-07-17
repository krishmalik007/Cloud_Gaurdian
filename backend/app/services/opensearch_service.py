from opensearchpy import OpenSearch, ConnectionError as OSConnectionError, TransportError
from app.logger import logger


class OpenSearchService:
    """
    Handles all interactions with the OpenSearch cluster.
    Uses lazy initialization to avoid crashing if settings are unavailable at import time.
    """

    def __init__(self):
        self._client: OpenSearch | None = None

    def _get_client(self) -> OpenSearch:
        """Lazily initialize the OpenSearch client on first use."""
        if self._client is None:
            from app.config import get_settings

            settings = get_settings()
            self._client = OpenSearch(
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
                verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
            )
        return self._client

    @property
    def client(self) -> OpenSearch:
        """Public accessor for the OpenSearch client."""
        return self._get_client()

    def ping(self) -> bool:
        """Check if OpenSearch is reachable."""
        try:
            if self.client.ping():
                logger.info("Connected to OpenSearch successfully.")
                return True

            logger.error("Unable to connect to OpenSearch.")
            return False

        except OSConnectionError as e:
            logger.error(f"OpenSearch connection refused: {e}")
            return False
        except TransportError as e:
            logger.error(f"OpenSearch transport error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected OpenSearch error: {e}")
            return False

    def index_document(self, index: str, body: dict, doc_id: str | None = None) -> dict:
        """Index a document into OpenSearch."""
        try:
            response = self.client.index(index=index, body=body, id=doc_id)
            logger.info(f"Document indexed in '{index}': {response.get('_id')}")
            return response
        except (OSConnectionError, TransportError) as e:
            logger.error(f"Failed to index document: {e}")
            raise

    def search(self, index: str, query: dict) -> dict:
        """Search documents in an OpenSearch index."""
        try:
            response = self.client.search(index=index, body=query)
            return response
        except (OSConnectionError, TransportError) as e:
            logger.error(f"Search failed on index '{index}': {e}")
            raise

    def create_index(self, index: str, body: dict | None = None) -> bool:
        """Create an OpenSearch index with optional mappings."""
        try:
            if not self.client.indices.exists(index=index):
                self.client.indices.create(index=index, body=body or {})
                logger.info(f"Index '{index}' created successfully.")
                return True
            logger.info(f"Index '{index}' already exists.")
            return False
        except (OSConnectionError, TransportError) as e:
            logger.error(f"Failed to create index '{index}': {e}")
            raise

    def cluster_health(self) -> dict | None:
        """Get OpenSearch cluster health status."""
        try:
            return self.client.cluster.health()
        except (OSConnectionError, TransportError) as e:
            logger.error(f"Failed to get cluster health: {e}")
            return None


# Singleton instance — lazily initialized
opensearch_service = OpenSearchService()