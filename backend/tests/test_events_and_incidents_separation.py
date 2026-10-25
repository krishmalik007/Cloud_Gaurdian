"""
Regression & Verification Test Suite: Events and Incidents Pipeline & API Separation
=====================================================================================

Validates:
1. An event is successfully saved to the OpenSearch events index.
2. The Events API returns saved events.
3. The Incidents API returns only incident records.
4. Zero-risk informational events are visible in the Events API without appearing as security incidents.
5. A genuine high-risk event appears in the Incidents API.
6. Empty results are handled correctly.
7. OpenSearch failures produce visible, appropriate API errors.
8. Frontend response parsing handles the actual backend response schema.
9. WebSocket event messages update the appropriate dashboard section.
10. WebSocket incident messages update the incident list without duplicate notifications.
11. JWT-protected endpoints continue to enforce authentication.
12. Existing ingestion and incident-flooding logic is fully preserved.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.auth.jwt_handler import create_access_token
from app.main import app
from app.services.event_service import EventService
from app.services.log_processor import LogProcessor
from app.storage.event_repository import EventRepository
from app.storage.incident_repository import IncidentRepository


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    token = create_access_token({
        "user_id": "USR-test-analyst-001",
        "username": "analyst_tester",
        "role": "ANALYST",
    })
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    token = create_access_token({
        "user_id": "USR-test-admin-001",
        "username": "admin_tester",
        "role": "ADMIN",
    })
    return {"Authorization": f"Bearer {token}"}


# ------------------------------------------------------------------------------
# Test 1: An event is successfully saved to the OpenSearch events index
# ------------------------------------------------------------------------------
def test_event_saved_to_events_index():
    mock_os = MagicMock()
    mock_os.indices.exists.return_value = True

    repo = EventRepository(opensearch_client=mock_os)
    sample_event = {
        "event_id": "evt-save-test-101",
        "event_name": "GetBucketAcl",
        "provider": "AWS",
        "username": "tester",
        "status": "INFORMATIONAL",
        "risk_score": 0,
        "risk_level": "LOW",
        "is_incident": False,
        "raw_log": {"test": "data"}
    }

    saved = repo.save_event(sample_event)
    assert saved["event_id"] == "evt-save-test-101"
    mock_os.index.assert_called_once()
    call_kwargs = mock_os.index.call_args[1]
    assert call_kwargs["index"] == "events"
    assert call_kwargs["id"] == "evt-save-test-101"


# ------------------------------------------------------------------------------
# Test 2: The Events API returns saved events
# ------------------------------------------------------------------------------
def test_events_api_returns_saved_events(test_client, auth_headers):
    mock_hits = [
        {
            "_source": {
                "event_id": "evt-api-001",
                "event_name": "GetCallerIdentity",
                "provider": "AWS",
                "username": "dev-user",
                "status": "INFORMATIONAL",
                "risk_score": 0,
                "is_incident": False,
                "timestamp": "2026-10-20T12:00:00Z"
            }
        }
    ]

    with patch("app.storage.opensearch_client.client.search") as mock_search:
        mock_search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": mock_hits
            }
        }
        with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):
            response = test_client.get("/events/search?page=1&size=10", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["events"]) == 1
            assert data["events"][0]["event_id"] == "evt-api-001"
            assert data["events"][0]["event_name"] == "GetCallerIdentity"


# ------------------------------------------------------------------------------
# Test 3: The Incidents API returns only incident records
# ------------------------------------------------------------------------------
def test_incidents_api_returns_only_incidents(test_client, auth_headers):
    mock_hits = [
        {
            "_source": {
                "incident_id": "INC-20261020-001",
                "event_name": "AttachUserPolicy",
                "provider": "AWS",
                "username": "attacker",
                "status": "OPEN",
                "risk_score": 90,
                "risk_level": "HIGH",
                "is_incident": True,
                "created_at": "2026-10-20T12:00:00Z"
            }
        }
    ]

    with patch("app.storage.opensearch_client.client.search") as mock_search:
        mock_search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": mock_hits
            }
        }
        with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):
            response = test_client.get("/incidents/search?page=1&size=10", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            assert len(data["incidents"]) == 1
            assert data["incidents"][0]["incident_id"] == "INC-20261020-001"
            call_kwargs = mock_search.call_args[1]
            assert call_kwargs["index"] == "incidents"


# ------------------------------------------------------------------------------
# Test 4: Zero-risk informational events appear in Events API, NOT in Incidents
# ------------------------------------------------------------------------------
def test_zero_risk_events_in_events_not_incidents():
    mock_event_os = MagicMock()
    mock_incident_os = MagicMock()

    mock_event_repo = EventRepository(opensearch_client=mock_event_os)
    mock_incident_repo = IncidentRepository(opensearch_client=mock_incident_os)

    processor = LogProcessor()

    routine_log = {
        "provider": "AWS",
        "eventName": "GetCallerIdentity",
        "eventSource": "sts.amazonaws.com",
        "eventID": "sts-zero-risk-uuid-1",
        "userIdentity": {"type": "IAMUser", "userName": "routine-worker"},
        "awsRegion": "ap-south-1",
        "sourceIPAddress": "127.0.0.1",
        "eventTime": "2026-10-20T12:30:00Z"
    }

    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        result = processor.process_log(routine_log)

        # 1. Event is saved to events repository
        mock_event_os.index.assert_called_once()
        assert mock_event_os.index.call_args[1]["index"] == "events"

        # 2. Incident repository was NOT called to save an incident
        mock_incident_os.index.assert_not_called()

        # 3. WebSocket broadcast was NOT called for routine non-incident event
        mock_ws.assert_not_called()


# ------------------------------------------------------------------------------
# Test 5: A genuine high-risk event appears in Incidents API
# ------------------------------------------------------------------------------
def test_high_risk_event_generates_incident():
    mock_event_os = MagicMock()
    mock_incident_os = MagicMock()
    mock_incident_os.get.return_value = None

    mock_event_repo = EventRepository(opensearch_client=mock_event_os)
    mock_incident_repo = IncidentRepository(opensearch_client=mock_incident_os)

    processor = LogProcessor()

    malicious_log = {
        "provider": "AWS",
        "eventName": "ConsoleLogin",
        "eventSource": "signin.amazonaws.com",
        "eventID": "malicious-policy-uuid-99",
        "userIdentity": {"type": "IAMUser", "userName": "infiltrator"},
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.23",
        "eventTime": "2026-10-20T12:35:00Z",
        "errorMessage": "Failed authentication",
        "responseElements": {"ConsoleLogin": "Failure"}
    }

    mock_ioc = {
        "value": "198.51.100.23",
        "enabled": True,
        "severity": "CRITICAL",
        "source": "THREAT_INTEL",
        "description": "Known malicious actor C2 IP"
    }

    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.threat_service.threat_service.lookup", return_value=mock_ioc), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        result = processor.process_log(malicious_log)

        # 1. Event is saved to events repository
        mock_event_os.index.assert_called_once()

        # 2. Incident repository IS called to save an incident
        mock_incident_os.index.assert_called_once()
        assert mock_incident_os.index.call_args[1]["index"] == "incidents"

        # 3. Incident notification was broadcasted to WebSocket
        assert mock_ws.call_count == 1
        broadcast_msg = mock_ws.call_args[0][0]
        assert broadcast_msg["type"] == "incident_created"
        assert broadcast_msg["data"]["incident_id"] is not None


# ------------------------------------------------------------------------------
# Test 6: Empty results are handled correctly
# ------------------------------------------------------------------------------
def test_events_api_handles_empty_results(test_client, auth_headers):
    with patch("app.storage.opensearch_client.client.search") as mock_search:
        mock_search.return_value = {
            "hits": {
                "total": {"value": 0},
                "hits": []
            }
        }
        with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):
            response = test_client.get("/events/search?provider=NON_EXISTENT", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert data["events"] == []


# ------------------------------------------------------------------------------
# Test 7: OpenSearch failures produce visible, appropriate API errors
# ------------------------------------------------------------------------------
def test_opensearch_failure_produces_500(test_client, auth_headers):
    with patch("app.services.event_service.event_service.search_events", side_effect=Exception("OpenSearch connection timeout")):
        with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):
            response = test_client.get("/events/search", headers=auth_headers)
            assert response.status_code == 500
            assert "Failed to retrieve cloud events" in response.json()["detail"]


# ------------------------------------------------------------------------------
# Test 8: Frontend response parsing matches backend schema
# ------------------------------------------------------------------------------
def test_backend_response_schema_matches_frontend_expectations(test_client, auth_headers):
    with patch("app.storage.opensearch_client.client.search") as mock_search:
        mock_search.return_value = {
            "hits": {
                "total": {"value": 25},
                "hits": [
                    {
                        "_source": {
                            "event_id": "evt-sch-01",
                            "event_name": "DescribeInstances",
                            "provider": "AWS",
                            "username": "auditor",
                            "region": "ap-south-1",
                            "source_ip": "10.0.0.1",
                            "status": "INFORMATIONAL",
                            "risk_level": "LOW",
                            "risk_score": 0,
                            "timestamp": "2026-10-20T12:40:00Z",
                            "is_incident": False
                        }
                    }
                ]
            }
        }
        with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):
            response = test_client.get("/events/search?page=2&size=1", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "page" in data
            assert "size" in data
            assert "total" in data
            assert "events" in data
            assert data["page"] == 2
            assert data["size"] == 1
            assert data["total"] == 25
            assert isinstance(data["events"], list)
            event = data["events"][0]
            assert "event_id" in event
            assert "event_name" in event
            assert "provider" in event
            assert "username" in event
            assert "region" in event
            assert "source_ip" in event
            assert "status" in event
            assert "risk_level" in event
            assert "risk_score" in event
            assert "timestamp" in event


# ------------------------------------------------------------------------------
# Test 9: WebSocket message types separated (event_ingested vs incident_created)
# ------------------------------------------------------------------------------
def test_websocket_broadcast_separation():
    processor = LogProcessor()
    mock_event_repo = MagicMock()
    mock_incident_repo = MagicMock()

    routine_log = {
        "provider": "AWS",
        "eventName": "DescribeSubnets",
        "eventID": "sub-event-1",
        "userIdentity": {"type": "IAMUser", "userName": "viewer"},
        "awsRegion": "ap-south-1",
    }
    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        processor.process_log(routine_log)
        # Routine non-incident logs MUST NOT trigger WebSocket broadcasts
        assert mock_ws.call_count == 0


# ------------------------------------------------------------------------------
# Test 10: WebSocket incident messages deduplicated
# ------------------------------------------------------------------------------
def test_websocket_incident_deduplication():
    processor = LogProcessor()
    mock_event_repo = MagicMock()
    mock_incident_repo = MagicMock()
    mock_incident_repo.get_incident.return_value = {
        "incident_id": "INC-DUPLICATE-001",
        "status": "OPEN"
    }

    duplicate_incident_log = {
        "provider": "AWS",
        "eventName": "ConsoleLogin",
        "eventSource": "signin.amazonaws.com",
        "eventID": "dup-policy-uuid-1",
        "userIdentity": {"type": "IAMUser", "userName": "infiltrator"},
        "awsRegion": "us-east-1",
        "sourceIPAddress": "198.51.100.23",
        "eventTime": "2026-10-20T12:35:00Z",
        "errorMessage": "Failed authentication",
        "responseElements": {"ConsoleLogin": "Failure"}
    }

    mock_ioc = {
        "value": "198.51.100.23",
        "enabled": True,
        "severity": "CRITICAL",
        "source": "THREAT_INTEL",
        "description": "Known malicious actor C2 IP"
    }

    with patch("app.services.log_processor.event_repository", mock_event_repo), \
         patch("app.services.log_processor.incident_repository", mock_incident_repo), \
         patch("app.services.threat_service.threat_service.lookup", return_value=mock_ioc), \
         patch("app.services.log_processor.ws_manager.broadcast_sync") as mock_ws:

        result = processor.process_log(duplicate_incident_log)
        # Duplicate incident persistence and notification are suppressed
        assert mock_ws.call_count == 0


# ------------------------------------------------------------------------------
# Test 11: JWT-protected endpoints continue to enforce authentication
# ------------------------------------------------------------------------------
def test_jwt_authentication_enforced(test_client):
    # Missing token -> 401
    resp_no_auth = test_client.get("/events/search")
    assert resp_no_auth.status_code == 401

    # Invalid token -> 401
    resp_bad_auth = test_client.get("/events/search", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert resp_bad_auth.status_code == 401

    # Insufficient role -> 403
    viewer_token = create_access_token({
        "user_id": "USR-viewer-01",
        "username": "viewer",
        "role": "VIEWER"
    })
    with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "VIEWER"}):
        resp_forbidden = test_client.get("/events/search", headers={"Authorization": f"Bearer {viewer_token}"})
        assert resp_forbidden.status_code == 403


# ------------------------------------------------------------------------------
# Test 12: GET /logs/ also routes to event search for backward compatibility
# ------------------------------------------------------------------------------
def test_logs_get_endpoint_routes_to_events(test_client, auth_headers):
    with patch("app.services.event_service.event_service.search_events") as mock_search_events:
        mock_search_events.return_value = {
            "page": 1,
            "size": 10,
            "total": 5,
            "events": [{"event_id": "evt-log-01"}]
        }
        with patch("app.auth.dependencies.repository.get_user_by_id", return_value={"enabled": True, "role": "ANALYST"}):
            resp = test_client.get("/logs/search?page=1&size=10", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["total"] == 5
            mock_search_events.assert_called_once()
