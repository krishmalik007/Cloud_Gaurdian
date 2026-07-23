from opensearchpy import OpenSearch

from app.config import get_settings

settings = get_settings()

client = OpenSearch(
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