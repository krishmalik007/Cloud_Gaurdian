import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.session_repository import session_repository
import uuid
from datetime import datetime, timezone, timedelta

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_sessions():
    """Clear sessions before and after tests."""
    try:
        session_repository.client.delete_by_query(
            index=session_repository.INDEX_NAME,
            body={"query": {"match_all": {}}},
            refresh=True
        )
    except Exception:
        pass
    yield
    try:
        session_repository.client.delete_by_query(
            index=session_repository.INDEX_NAME,
            body={"query": {"match_all": {}}},
            refresh=True
        )
    except Exception:
        pass

def test_session_tracking_logic():
    # Helper to insert direct sessions for testing expiry and users
    def add_session(user_id, role, expired=False):
        sid = str(uuid.uuid4())
        expiry = datetime.now(timezone.utc)
        if expired:
            expiry = expiry - timedelta(days=1)
        else:
            expiry = expiry + timedelta(days=1)
        
        session_repository.create_session(sid, user_id, role, expiry.isoformat())
        # Refresh index manually
        session_repository.client.indices.refresh(index=session_repository.INDEX_NAME)
        return sid

    # Initial state
    assert session_repository.count_active_analyst_users() == 0
    
    # 1. ADMIN login -> does NOT increase
    s_admin = add_session("ADMIN_1", "ADMIN")
    assert session_repository.count_active_analyst_users() == 0
    
    # 2. ANALYST login -> increases by 1
    s_analyst1_a = add_session("ANALYST_1", "ANALYST")
    assert session_repository.count_active_analyst_users() == 1
    
    # 3. Same ANALYST opens another tab -> remains 1
    s_analyst1_b = add_session("ANALYST_1", "ANALYST")
    assert session_repository.count_active_analyst_users() == 1
    
    # 4. Second different ANALYST logs in -> becomes 2
    s_analyst2 = add_session("ANALYST_2", "ANALYST")
    assert session_repository.count_active_analyst_users() == 2
    
    # 5. ANALYST logout -> decreases by 1
    # First, let's remove both sessions for ANALYST_1
    session_repository.delete_session(s_analyst1_a)
    session_repository.delete_session(s_analyst1_b)
    # Refresh
    session_repository.client.indices.refresh(index=session_repository.INDEX_NAME)
    assert session_repository.count_active_analyst_users() == 1
    
    # 6. Expired session -> not counted
    s_analyst3_expired = add_session("ANALYST_3", "ANALYST", expired=True)
    assert session_repository.count_active_analyst_users() == 1

