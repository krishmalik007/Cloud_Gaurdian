import pytest
from unittest.mock import patch, MagicMock

import importlib
import app.storage.opensearch_client

def test_shared_client_configuration_no_ca():
    with patch("app.storage.opensearch_client.settings.OPENSEARCH_HOST", "test-host"), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_PORT", 9999), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_USERNAME", "test-user"), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_PASSWORD", "test-pass"), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_USE_SSL", True), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_VERIFY_CERTS", False), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_CA_CERTS", None):
        
        with patch("opensearchpy.OpenSearch") as mock_os:
            importlib.reload(app.storage.opensearch_client)
            
            mock_os.assert_called_once_with(
                hosts=[{"host": "test-host", "port": 9999}],
                http_auth=("test-user", "test-pass"),
                use_ssl=True,
                verify_certs=False
            )
            # CA certs should not be passed
            assert "ca_certs" not in mock_os.call_args[1]

def test_shared_client_configuration_with_ca():
    with patch("app.storage.opensearch_client.settings.OPENSEARCH_HOST", "test-host"), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_PORT", 9999), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_USERNAME", "test-user"), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_PASSWORD", "test-pass"), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_USE_SSL", True), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_VERIFY_CERTS", True), \
         patch("app.storage.opensearch_client.settings.OPENSEARCH_CA_CERTS", "/path/to/ca.pem"):
        
        with patch("opensearchpy.OpenSearch") as mock_os:
            importlib.reload(app.storage.opensearch_client)
            
            mock_os.assert_called_once_with(
                hosts=[{"host": "test-host", "port": 9999}],
                http_auth=("test-user", "test-pass"),
                use_ssl=True,
                verify_certs=True,
                ca_certs="/path/to/ca.pem"
            )

def test_opensearch_service_reuses_shared_client():
    # Reload the opensearch_service module to ensure it picks up the shared client
    import app.services.opensearch_service
    importlib.reload(app.services.opensearch_service)
    
    from app.services.opensearch_service import opensearch_service, OpenSearchService
    from app.storage.opensearch_client import client as shared_client
    
    assert opensearch_service.client is shared_client
    
    # Also verify instantiating a new service uses the same shared client
    new_service = OpenSearchService()
    assert new_service.client is shared_client

    # Clean up module state
    importlib.reload(app.storage.opensearch_client)
    importlib.reload(app.services.opensearch_service)
