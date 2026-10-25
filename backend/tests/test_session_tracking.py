import pytest
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.storage.session_repository import session_repository
from app.storage.user_repository import UserRepository
from app.auth.password import hash_password
from app.auth.jwt_handler import verify_access_token

client = TestClient(app)
user_repo = UserRepository()


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clear test sessions and users before and after each test."""
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


def test_session_tracking_unit_scenarios():
    """
    Unit test covering:
    - one analyst / one session -> 1
    - one analyst / two sessions -> 1
    - two analysts / multiple sessions -> 2
    - logout removes one user's active session correctly
    - expired session excluded
    - non-ANALYST roles excluded
    """
    def add_session(user_id, role, expired=False):
        sid = str(uuid.uuid4())
        expiry = datetime.now(timezone.utc)
        if expired:
            expiry = expiry - timedelta(days=1)
        else:
            expiry = expiry + timedelta(days=1)

        session_repository.create_session(sid, user_id, role, expiry.isoformat())
        session_repository.client.indices.refresh(index=session_repository.INDEX_NAME)
        return sid

    # Initial state
    assert session_repository.count_active_analyst_users() == 0

    # 1. ADMIN login -> does NOT count toward active analysts
    s_admin = add_session("ADMIN_USER_1", "ADMIN")
    assert session_repository.count_active_analyst_users() == 0

    # 2. Analyst A (1 session) -> 1
    s_analyst_a1 = add_session("ANALYST_USER_A", "ANALYST")
    assert session_repository.count_active_analyst_users() == 1

    # 3. Analyst A (2nd session from browser 2) -> remains 1 (distinct user)
    s_analyst_a2 = add_session("ANALYST_USER_A", "ANALYST")
    assert session_repository.count_active_analyst_users() == 1

    # 4. Analyst B (1 session) -> becomes 2
    s_analyst_b1 = add_session("ANALYST_USER_B", "ANALYST")
    assert session_repository.count_active_analyst_users() == 2

    # 5. Analyst A logs out from session 1 -> still 2 (Analyst A still has session 2, Analyst B has session 1)
    session_repository.delete_session(s_analyst_a1)
    session_repository.client.indices.refresh(index=session_repository.INDEX_NAME)
    assert session_repository.count_active_analyst_users() == 2

    # 6. Analyst A logs out from session 2 -> becomes 1 (only Analyst B active)
    session_repository.delete_session(s_analyst_a2)
    session_repository.client.indices.refresh(index=session_repository.INDEX_NAME)
    assert session_repository.count_active_analyst_users() == 1

    # 7. Expired session added for Analyst C -> still 1
    s_analyst_c_exp = add_session("ANALYST_USER_C", "ANALYST", expired=True)
    assert session_repository.count_active_analyst_users() == 1

    # 8. Analyst B logs out -> becomes 0
    session_repository.delete_session(s_analyst_b1)
    session_repository.client.indices.refresh(index=session_repository.INDEX_NAME)
    assert session_repository.count_active_analyst_users() == 0


def test_full_auth_session_lifecycle_sequence():
    """
    Exact requirement verification sequence:
    TEST 1: Analyst A Browser 1 -> Expected = 1
    TEST 2: Analyst A Browser 2 -> Expected = 1
    TEST 3: Analyst B logs in -> Expected = 2
    TEST 4: Analyst A logs out from Browser 1 and Browser 2 -> Expected = 1
    TEST 5: Refresh Analyst B's access token -> Expected = 1 (no duplicate session, same session_id)
    TEST 6: Log Analyst B out -> Expected = 0
    """
    # Create test users in repository
    user_a = {
        "user_id": "USR-TEST-ANALYST-A",
        "username": "analyst_a",
        "email": "analyst_a@cloudguardian.io",
        "password": hash_password("Password123!"),
        "role": "ANALYST",
        "enabled": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    user_b = {
        "user_id": "USR-TEST-ANALYST-B",
        "username": "analyst_b",
        "email": "analyst_b@cloudguardian.io",
        "password": hash_password("Password123!"),
        "role": "ANALYST",
        "enabled": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    user_repo.create_user(user_a)
    user_repo.create_user(user_b)
    user_repo.client.indices.refresh(index=user_repo.INDEX_NAME)

    try:
        # Initial active analysts check
        res = client.get("/dashboard/active-analysts", headers={
            "Authorization": f"Bearer {client.post('/auth/login', json={'email': user_a['email'], 'password': 'Password123!'}).json()['access_token']}"
        })
        # Note: the above login created 1 session
        assert res.status_code == 200
        assert res.json()["count"] == 1

        # Clear session to start clean sequence
        session_repository.client.delete_by_query(
            index=session_repository.INDEX_NAME,
            body={"query": {"match_all": {}}},
            refresh=True
        )

        # ----------------------------------------------------
        # TEST 1: Analyst A logs in from Browser 1 -> Expected = 1
        # ----------------------------------------------------
        login_a1 = client.post("/auth/login", json={"email": "analyst_a@cloudguardian.io", "password": "Password123!"})
        assert login_a1.status_code == 200
        token_a1 = login_a1.json()["access_token"]
        session_id_a1 = verify_access_token(token_a1)["session_id"]
        assert session_id_a1 is not None

        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {token_a1}"})
        assert stats.status_code == 200
        assert stats.json()["count"] == 1

        # ----------------------------------------------------
        # TEST 2: Analyst A logs in from Browser 2 -> Expected = 1 (distinct user)
        # ----------------------------------------------------
        login_a2 = client.post("/auth/login", json={"email": "analyst_a@cloudguardian.io", "password": "Password123!"})
        assert login_a2.status_code == 200
        token_a2 = login_a2.json()["access_token"]
        session_id_a2 = verify_access_token(token_a2)["session_id"]
        assert session_id_a2 != session_id_a1

        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {token_a2}"})
        assert stats.json()["count"] == 1

        # ----------------------------------------------------
        # TEST 3: Analyst B logs in -> Expected = 2
        # ----------------------------------------------------
        login_b = client.post("/auth/login", json={"email": "analyst_b@cloudguardian.io", "password": "Password123!"})
        assert login_b.status_code == 200
        token_b = login_b.json()["access_token"]
        refresh_b = login_b.json()["refresh_token"]
        session_id_b = verify_access_token(token_b)["session_id"]

        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {token_b}"})
        assert stats.json()["count"] == 2

        # ----------------------------------------------------
        # TEST 4: Analyst A logs out from both Browser 1 and Browser 2 -> Expected = 1
        # ----------------------------------------------------
        # Logout Browser 1
        logout_a1 = client.post("/auth/logout", headers={"Authorization": f"Bearer {token_a1}"})
        assert logout_a1.status_code == 200
        # Count is still 2 because Browser 2 session for Analyst A is still active
        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {token_b}"})
        assert stats.json()["count"] == 2

        # Logout Browser 2
        logout_a2 = client.post("/auth/logout", headers={"Authorization": f"Bearer {token_a2}"})
        assert logout_a2.status_code == 200
        # Now Analyst A has no active sessions, only Analyst B -> Expected = 1
        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {token_b}"})
        assert stats.json()["count"] == 1

        # ----------------------------------------------------
        # TEST 5: Refresh Analyst B's access token -> Expected = 1 (no duplicate session, same session_id)
        # ----------------------------------------------------
        refresh_res = client.post("/auth/refresh", json={"refresh_token": refresh_b})
        assert refresh_res.status_code == 200
        refreshed_token_b = refresh_res.json()["access_token"]
        refreshed_payload = verify_access_token(refreshed_token_b)
        assert refreshed_payload["session_id"] == session_id_b

        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {refreshed_token_b}"})
        assert stats.json()["count"] == 1

        # ----------------------------------------------------
        # TEST 6: Log Analyst B out -> Expected = 0
        # ----------------------------------------------------
        logout_b = client.post("/auth/logout", headers={"Authorization": f"Bearer {refreshed_token_b}"})
        assert logout_b.status_code == 200

        # Create an admin user so get_current_user validates successfully
        admin_user = {
            "user_id": "USR-TEST-ADMIN",
            "username": "admin_test",
            "email": "admin_test@cloudguardian.io",
            "password": hash_password("Password123!"),
            "role": "ADMIN",
            "enabled": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        user_repo.create_user(admin_user)
        user_repo.client.indices.refresh(index=user_repo.INDEX_NAME)

        admin_login = client.post("/auth/login", json={"email": "admin_test@cloudguardian.io", "password": "Password123!"})
        admin_token = admin_login.json()["access_token"]
        stats = client.get("/dashboard/active-analysts", headers={"Authorization": f"Bearer {admin_token}"})
        assert stats.status_code == 200
        assert stats.json()["count"] == 0

    finally:
        # Clean up test users
        try:
            user_repo.client.delete(index=user_repo.INDEX_NAME, id=user_a["user_id"], refresh=True, ignore=[404])
            user_repo.client.delete(index=user_repo.INDEX_NAME, id=user_b["user_id"], refresh=True, ignore=[404])
            user_repo.client.delete(index=user_repo.INDEX_NAME, id="USR-TEST-ADMIN", refresh=True, ignore=[404])
        except Exception:
            pass
