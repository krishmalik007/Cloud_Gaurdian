import pytest
from app.storage.incident_repository import incident_repository
from app.storage.opensearch_client import client

def test_incident_index_mapping():
    """
    Verify that the incidents index is created with the required mapping fields.
    This ensures created_at and other keyword fields exist to support sorting and aggregation.
    """
    index_name = incident_repository.INDEX_NAME
    
    # Temporarily delete the index to test recreation
    if client.indices.exists(index=index_name):
        from opensearchpy import OpenSearch
        from app.config import get_settings
        settings = get_settings()
        admin_client = OpenSearch(
            hosts=[{"host": settings.OPENSEARCH_HOST, "port": settings.OPENSEARCH_PORT}],
            http_auth=("admin", "CloudGuardianAdmin123!"),
            use_ssl=settings.OPENSEARCH_USE_SSL,
            verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
            ca_certs=settings.OPENSEARCH_CA_CERTS
        )
        admin_client.indices.delete(index=index_name)
    incident_repository.__init__()
    
    # Assert index exists
    assert client.indices.exists(index=index_name)
    
    # Fetch mapping
    mapping = client.indices.get_mapping(index=index_name)
    properties = mapping[index_name]["mappings"]["properties"]
    
    # Verify exact types
    assert properties["created_at"]["type"] == "date"
    assert properties["status"]["type"] == "text"
    assert "keyword" in properties["status"]["fields"]
    
    assert properties["risk_level"]["type"] == "text"
    assert "keyword" in properties["risk_level"]["fields"]
    
    assert properties["provider"]["type"] == "text"
    assert "keyword" in properties["provider"]["fields"]
    
    assert properties["username"]["type"] == "text"
    assert "keyword" in properties["username"]["fields"]
    
    assert properties["incident_id"]["type"] == "keyword"
    assert properties["risk_score"]["type"] == "long"
