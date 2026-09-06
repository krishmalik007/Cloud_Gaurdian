import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from unittest.mock import patch, MagicMock

from app.main import app
from app.services.websocket_manager import ws_manager
from app.services.log_processor import log_processor
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.storage.incident_repository import IncidentRepository


@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch('app.storage.incident_repository.IncidentRepository.save_incident') as mock_save:
        with patch('app.pipeline.incident_pipeline.IncidentPipeline.process_event') as mock_pipeline:
            with patch('app.storage.user_repository.UserRepository.get_user_by_id') as mock_get_user:
                with patch('app.services.aws_sqs_consumer.sqs_consumer.start') as mock_sqs_start:
                    # We don't want the actual background tasks running for unit tests
                    mock_get_user.return_value = {"user_id": "test", "role": "ANALYST"}
                    yield {
                        'save_incident': mock_save,
                        'process_event': mock_pipeline,
                        'get_user_by_id': mock_get_user,
                        'sqs_start': mock_sqs_start
                    }


@pytest.fixture
def client():
    # Clear active connections between tests
    ws_manager.active_connections = []
    # Using TestClient as a context manager triggers @app.on_event("startup")
    # which correctly initializes ws_manager.loop with the active running loop.
    with TestClient(app) as client:
        yield client


@pytest.fixture
def valid_token():
    return create_access_token({"user_id": "test", "role": "ANALYST"})


@pytest.fixture
def invalid_role_token():
    return create_access_token({"user_id": "test", "role": "USER"})


@pytest.fixture
def refresh_token():
    return create_refresh_token({"user_id": "test", "role": "ANALYST"})


def test_websocket_connects_with_valid_token(client, valid_token):
    with client.websocket_connect("/ws/dashboard") as websocket:
        # Send first message for auth
        websocket.send_json({"token": valid_token})
        assert websocket.receive_json() == {"status": "authenticated"}
        
        # Verify it's connected by checking manager
        assert len(ws_manager.active_connections) == 1
        
        websocket.close()


def test_websocket_rejects_missing_token(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/dashboard") as websocket:
            websocket.send_json({})
            websocket.receive_text() # This should trigger the exception

    assert exc_info.value.code == 1008
    assert len(ws_manager.active_connections) == 0


def test_websocket_rejects_invalid_token(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/dashboard") as websocket:
            websocket.send_json({"token": "invalid.jwt.token"})
            websocket.receive_text()

    assert exc_info.value.code == 1008


def test_websocket_rejects_refresh_token(client, refresh_token):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/dashboard") as websocket:
            websocket.send_json({"token": refresh_token})
            websocket.receive_text()

    assert exc_info.value.code == 1008


def test_websocket_rejects_invalid_role(client, invalid_role_token):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/dashboard") as websocket:
            websocket.send_json({"token": invalid_role_token})
            websocket.receive_text()

    assert exc_info.value.code == 1008


def test_multiple_clients_and_broadcast(client, valid_token):
    # This test connects multiple clients and verifies they all receive a broadcast
    with client.websocket_connect("/ws/dashboard") as ws1:
        ws1.send_json({"token": valid_token})
        assert ws1.receive_json() == {"status": "authenticated"}
        
        with client.websocket_connect("/ws/dashboard") as ws2:
            ws2.send_json({"token": valid_token})
            assert ws2.receive_json() == {"status": "authenticated"}
            
            assert len(ws_manager.active_connections) == 2
            
            # Use broadcast_sync to correctly schedule onto the active background loop
            message = {"type": "test_broadcast"}
            ws_manager.broadcast_sync(message)
            
            data1 = ws1.receive_json()
            data2 = ws2.receive_json()
            
            assert data1 == message
            assert data2 == message


def test_incident_creation_triggers_broadcast(client, valid_token, mock_dependencies):
    mock_incident = {
        "incident_id": "INC-123",
        "status": "OPEN",
        "priority": "HIGH",
        "risk_score": 85,
        "risk_level": "HIGH",
        "username": "attacker",
        "provider": "AWS",
        "created_at": "2026-09-04T12:00:00Z",
        "threat_score": 50,
        "threat_level": "MEDIUM",
        "threat_tags": ["botnet"]
    }
    
    mock_dependencies['process_event'].return_value = mock_incident
    
    with client.websocket_connect("/ws/dashboard") as websocket:
        websocket.send_json({"token": valid_token})
        assert websocket.receive_json() == {"status": "authenticated"}
        
        # Simulate log processing (which should trigger broadcast_sync)
        # We need to run it synchronously
        incident = log_processor.process_log({"raw": "data"})
        
        assert incident == mock_incident
        mock_dependencies['save_incident'].assert_called_once_with(mock_incident)
        
        # We might need to yield to event loop for the threadsafe call to complete
        # in the test environment
        # Wait for the message
        data = websocket.receive_json()
        
        assert data["type"] == "incident_created"
        assert data["timestamp"] == "2026-09-04T12:00:00Z"
        assert data["data"]["incident_id"] == "INC-123"
        assert "responseElements.credentials" not in str(data)
        assert "secretAccessKey" not in str(data)


def test_websocket_failure_does_not_break_incident_creation(client, mock_dependencies):
    mock_incident = {
        "incident_id": "INC-123",
        "created_at": "2026-09-04T12:00:00Z",
    }
    mock_dependencies['process_event'].return_value = mock_incident
    
    # Introduce a failure in the broadcast mechanism
    with patch.object(ws_manager, 'broadcast_sync', side_effect=Exception("Broadcast failed!")):
        # Log processor should STILL succeed and return the incident
        incident = log_processor.process_log({"raw": "data"})
        
        assert incident == mock_incident
        mock_dependencies['save_incident'].assert_called_once_with(mock_incident)


def test_dashboard_rest_apis_still_work(client, valid_token):
    # Mock dashboard service to prevent DB calls
    with patch('app.services.dashboard_service.dashboard_service.get_summary', return_value={"total": 5}):
        response = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {valid_token}"})
        
        assert response.status_code == 200
        assert response.json() == {"total": 5}
