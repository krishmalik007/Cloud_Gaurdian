from opensearchpy import OpenSearch

from app.config import get_settings

settings = get_settings()

client_kwargs = {
    "hosts": [
        {
            "host": settings.OPENSEARCH_HOST,
            "port": settings.OPENSEARCH_PORT,
        }
    ],
    "http_auth": (
        settings.OPENSEARCH_USERNAME,
        settings.OPENSEARCH_PASSWORD,
    ),
    "use_ssl": settings.OPENSEARCH_USE_SSL,
    "verify_certs": settings.OPENSEARCH_VERIFY_CERTS,
}

if settings.OPENSEARCH_CA_CERTS:
    client_kwargs["ca_certs"] = settings.OPENSEARCH_CA_CERTS

client = OpenSearch(**client_kwargs)