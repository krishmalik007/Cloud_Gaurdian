import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect

from app.main import app, settings
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.schemas.auth import UserRegister
from app.schemas.user import UserRoleUpdate
from app.schemas.incident import IncidentStatusUpdate, IncidentCreate
from app.schemas.ioc import IOCCreate
from app.auth.jwt_handler import create_access_token

@pytest.fixture
def client():
    # Disable rate limiting for tests
    from app.routes.auth import limiter
    limiter.enabled = False
    c = TestClient(app)
    yield c
    limiter.enabled = True

@pytest.fixture
def auth_service():
    return AuthService()

@pytest.fixture
def audit_service():
    return AuditService()

# 1. USER ID UUID
def test_user_id_uuid(auth_service):
    with patch('app.storage.user_repository.UserRepository.get_user_by_email', return_value=None), \
         patch('app.storage.user_repository.UserRepository.create_user'), \
         patch('app.services.audit_service.audit_service.create_log'):
        
        user1 = UserRegister(username="usr1", email="u1@test.com", password="password")
        user2 = UserRegister(username="usr2", email="u2@test.com", password="password")
        
        res1 = auth_service.register_user(user1)
        res2 = auth_service.register_user(user2)
        
        assert res1["user_id"] != res2["user_id"]
        assert res1["user_id"].startswith("USR-")
        assert len(res1["user_id"]) == 12  # USR- + 8 chars

# 2. AUDIT ID UUID
def test_audit_id_uuid(audit_service):
    with patch('app.storage.audit_repository.AuditRepository.create_log'):
        res1 = audit_service.create_log("u1", "user1", "action1", "res1", "SUCCESS")
        res2 = audit_service.create_log("u2", "user2", "action2", "res2", "SUCCESS")
        
        assert res1["audit_id"] != res2["audit_id"]
        assert res1["audit_id"].startswith("AUD-")
        assert len(res1["audit_id"]) == 12

# 3. EMAIL VALIDATION
def test_email_validation():
    # Valid
    UserRegister(username="usr", email="test@example.com", password="password")
    
    # Invalid
    with pytest.raises(ValueError):
        UserRegister(username="usr", email="invalid-email", password="password")
        
    # Missing
    with pytest.raises(ValueError):
        UserRegister(username="usr", password="password")

# 4. ROLE VALIDATION
def test_role_validation():
    # Valid
    UserRoleUpdate(role="ADMIN")
    UserRoleUpdate(role="ANALYST")
    UserRoleUpdate(role="VIEWER")
    
    # Invalid
    with pytest.raises(ValueError):
        UserRoleUpdate(role="SUPERUSER")

# 5. INCIDENT STATUS VALIDATION
def test_incident_status_validation():
    # Valid
    IncidentStatusUpdate(status="OPEN")
    IncidentStatusUpdate(status="INVESTIGATING")
    IncidentStatusUpdate(status="RESOLVED")
    
    # Invalid
    with pytest.raises(ValueError):
        IncidentStatusUpdate(status="GARBAGE")

# 6. DASHBOARD LIMIT VALIDATION
def test_dashboard_limit_validation(client):
    from app.auth.jwt_handler import create_access_token
    token = create_access_token({"user_id": "test_user", "role": "ADMIN"})
    
    with patch("app.storage.user_repository.UserRepository.get_user_by_id", return_value={"user_id": "test_user", "role": "ADMIN", "enabled": True}):
        res_valid = client.get("/dashboard/recent-incidents?limit=50", headers={"Authorization": f"Bearer {token}"})
        assert res_valid.status_code != 422
        
        res_invalid = client.get("/dashboard/recent-incidents?limit=99999", headers={"Authorization": f"Bearer {token}"})
        assert res_invalid.status_code == 422
        
        res_invalid2 = client.get("/dashboard/recent-incidents?limit=0", headers={"Authorization": f"Bearer {token}"})
        assert res_invalid2.status_code == 422

# 7. IOC VALIDATION
def test_ioc_validation():
    # Valid
    IOCCreate(type="IP", value="1.1.1.1", severity="HIGH")
    
    # Invalid type
    with pytest.raises(ValueError):
        IOCCreate(type="INVALID_TYPE", value="1.1.1.1")
        
    # Invalid severity
    with pytest.raises(ValueError):
        IOCCreate(type="IP", value="1.1.1.1", severity="INVALID_SEV")

# 8. WEBSOCKET DISABLED-USER CHECK
def test_websocket_disabled_user_check():
    from app.main import app as fastapi_app
    valid_token = create_access_token({"user_id": "test_user", "role": "ANALYST"})
    
    # Test valid enabled user
    with patch('app.storage.user_repository.UserRepository.get_user_by_id', return_value={"enabled": True, "role": "ANALYST"}):
        with TestClient(fastapi_app).websocket_connect("/ws/dashboard") as websocket:
            websocket.send_json({"token": valid_token})
            assert websocket.receive_json() == {"status": "authenticated"}

    # Test disabled user
    with patch('app.storage.user_repository.UserRepository.get_user_by_id', return_value={"enabled": False, "role": "ANALYST"}):
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with TestClient(fastapi_app).websocket_connect("/ws/dashboard") as websocket:
                websocket.send_json({"token": valid_token})
                websocket.receive_text()
        assert exc_info.value.code == 1008
        
    # Test missing user
    with patch('app.storage.user_repository.UserRepository.get_user_by_id', return_value=None):
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with TestClient(fastapi_app).websocket_connect("/ws/dashboard") as websocket:
                websocket.send_json({"token": valid_token})
                websocket.receive_text()
        assert exc_info.value.code == 1008

# 9. OPENAPI / DOCS
def test_openapi_docs_exposure():
    from app.main import app as main_app
    import importlib
    import app.main
    
    # Test DEBUG=True
    with patch('app.main.settings.DEBUG', True):
        importlib.reload(app.main)
        from app.main import app as true_app
        assert true_app.docs_url == "/docs"
        client = TestClient(true_app)
        res = client.get("/")
        assert "documentation" in res.json()
        
    # Test DEBUG=False
    with patch('app.main.settings.DEBUG', False):
        importlib.reload(app.main)
        from app.main import app as false_app
        assert false_app.docs_url is None
        client = TestClient(false_app)
        res = client.get("/")
        assert "documentation" not in res.json()

# Restore original state
import importlib
import app.main
importlib.reload(app.main)
from app.main import app as restored_app
app = restored_app


# 10. USERIDENTITY PAYLOAD SAFETY
def test_useridentity_payload_safety():
    # Valid normal IAM
    valid_payload = {
        "provider": "AWS",
        "eventName": "Test",
        "eventTime": "2026-09-04T12:00:00Z",
        "userIdentity": {"userName": "krish"}
    }
    IncidentCreate(**valid_payload)
    
    # Valid assume role
    valid_assume = {
        "provider": "AWS",
        "eventName": "Test",
        "eventTime": "2026-09-04T12:00:00Z",
        "userIdentity": {"principalId": "AROA123456:session"}
    }
    IncidentCreate(**valid_assume)
    
    # Oversized payload
    oversized = valid_payload.copy()
    oversized["userIdentity"] = {"userName": "a" * 9000}
    with pytest.raises(ValueError, match="payload too large"):
        IncidentCreate(**oversized)
        
    # Deeply nested payload
    deep = valid_payload.copy()
    nested = {}
    current = nested
    for i in range(12):
        current["k"] = {}
        current = current["k"]
    deep["userIdentity"] = nested
    with pytest.raises(ValueError, match="payload too deep"):
        IncidentCreate(**deep)
