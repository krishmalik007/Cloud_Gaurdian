"""
Refresh Token Tests
===================

Pure unit tests for the refresh-token feature.

These tests:
- Do NOT connect to OpenSearch, Kafka, or AWS.
- Exercise jwt_handler functions directly.
- Exercise AuthService.refresh_access_token() with a mocked repository
  so OpenSearch is never required.
- Verify that access tokens are rejected by verify_refresh_token().
- Verify that refresh tokens are rejected by verify_access_token().
- Verify that no JWT token values are printed to stdout during tests.

Run with:
    python test_auth.py
"""

import io
import sys
import unittest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEST_PAYLOAD = {
    "user_id": "USR-test-001",
    "email": "test@example.com",
    "role": "ANALYST",
}

_ENABLED_USER = {
    "user_id": "USR-test-001",
    "username": "testuser",
    "email": "test@example.com",
    "role": "ANALYST",
    "enabled": True,
}

_DISABLED_USER = {**_ENABLED_USER, "enabled": False}


def _capture_stdout(fn, *args, **kwargs):
    """Run fn(*args, **kwargs) and return (result, captured_stdout_text)."""
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        result = fn(*args, **kwargs)
    finally:
        sys.stdout = old
    return result, buf.getvalue()


# ---------------------------------------------------------------------------
# JWT Handler Unit Tests
# ---------------------------------------------------------------------------

class TestJWTHandler(unittest.TestCase):

    # ------------------------------------------------------------------
    # Access token basics
    # ------------------------------------------------------------------

    def test_access_token_verifies_as_access(self):
        """A fresh access token must be accepted by verify_access_token."""
        token = create_access_token(_TEST_PAYLOAD)
        payload = verify_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["type"], "access")
        self.assertEqual(payload["user_id"], "USR-test-001")

    def test_access_token_rejected_by_verify_refresh(self):
        """An access token must NOT pass verify_refresh_token — security requirement."""
        token = create_access_token(_TEST_PAYLOAD)
        result = verify_refresh_token(token)
        self.assertIsNone(result, "Access token must not be accepted as a refresh token")

    def test_expired_access_token_rejected(self):
        """An access token with a past expiry must return None."""
        token = create_access_token(_TEST_PAYLOAD, expires_delta=timedelta(seconds=-1))
        result = verify_access_token(token)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Refresh token basics
    # ------------------------------------------------------------------

    def test_refresh_token_verifies_as_refresh(self):
        """A fresh refresh token must be accepted by verify_refresh_token."""
        token = create_refresh_token(_TEST_PAYLOAD)
        payload = verify_refresh_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["type"], "refresh")
        self.assertEqual(payload["user_id"], "USR-test-001")

    def test_refresh_token_rejected_by_verify_access(self):
        """A refresh token must NOT pass verify_access_token — security requirement."""
        token = create_refresh_token(_TEST_PAYLOAD)
        result = verify_access_token(token)
        self.assertIsNone(result, "Refresh token must not be accepted as an access token")

    def test_expired_refresh_token_rejected(self):
        """An expired refresh token must return None from verify_refresh_token."""
        # We must create a refresh token that has already expired.
        # The jwt_handler does not expose an expires_delta param for refresh tokens,
        # so we verify that the existing verify_token rejects expired tokens by
        # creating a custom token via jwt directly.
        import jwt as pyjwt
        from datetime import datetime, timezone
        from app.auth.jwt_handler import SECRET_KEY, ALGORITHM

        expired_payload = {
            **_TEST_PAYLOAD,
            "type": "refresh",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        }
        expired_token = pyjwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        result = verify_refresh_token(expired_token)
        self.assertIsNone(result)

    # ------------------------------------------------------------------
    # Invalid / tampered tokens
    # ------------------------------------------------------------------

    def test_garbage_token_rejected(self):
        """A random string must return None for both verifiers."""
        self.assertIsNone(verify_access_token("not.a.jwt"))
        self.assertIsNone(verify_refresh_token("not.a.jwt"))

    def test_wrong_signature_rejected(self):
        """A token signed with a different key must be rejected."""
        import jwt as pyjwt
        from datetime import datetime, timezone

        bad_token = pyjwt.encode(
            {**_TEST_PAYLOAD, "type": "access", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256",
        )
        self.assertIsNone(verify_access_token(bad_token))

    # ------------------------------------------------------------------
    # No token values in stdout during token creation
    # ------------------------------------------------------------------

    def test_no_token_printed_on_create_access(self):
        """create_access_token must not print the token value to stdout."""
        _, output = _capture_stdout(create_access_token, _TEST_PAYLOAD)
        # Token is a long base64 string — check nothing resembling a JWT is printed
        self.assertNotIn("eyJ", output, "JWT value must not appear in stdout")

    def test_no_token_printed_on_create_refresh(self):
        """create_refresh_token must not print the token value to stdout."""
        _, output = _capture_stdout(create_refresh_token, _TEST_PAYLOAD)
        self.assertNotIn("eyJ", output, "JWT value must not appear in stdout")


# ---------------------------------------------------------------------------
# AuthService.refresh_access_token() Unit Tests
# (UserRepository is mocked — no OpenSearch required)
# ---------------------------------------------------------------------------

class TestAuthServiceRefresh(unittest.TestCase):

    def _make_service_with_repo(self, repo_mock):
        """Build an AuthService whose repository is replaced by repo_mock."""
        # Patch UserRepository at the module level so __init__ uses our mock
        with patch("app.services.auth_service.UserRepository", return_value=repo_mock):
            from importlib import reload
            import app.services.auth_service as svc_module
            reload(svc_module)
            return svc_module.AuthService()

    def setUp(self):
        # Build a fresh refresh token for each test
        self.refresh_token = create_refresh_token(_TEST_PAYLOAD)

        # Build the mock repo
        self.mock_repo = MagicMock()
        self.mock_repo.get_user_by_id.return_value = _ENABLED_USER

        # Patch AuditService so we don't need an OpenSearch connection
        self.audit_patcher = patch("app.services.auth_service.audit_service")
        self.mock_audit = self.audit_patcher.start()

        # Patch UserRepository.__init__ to be a no-op, then replace
        # service.repository with our mock after construction.
        self.repo_patcher = patch(
            "app.services.auth_service.UserRepository",
            return_value=self.mock_repo
        )
        self.repo_patcher.start()

        from app.services.auth_service import AuthService
        self.service = AuthService()
        # Belt-and-suspenders: make sure the instance really uses our mock
        self.service.repository = self.mock_repo

    def tearDown(self):
        self.audit_patcher.stop()
        self.repo_patcher.stop()

    # ------------------------------------------------------------------
    # Happy path
    # ------------------------------------------------------------------

    def test_valid_refresh_returns_new_access_token(self):
        """A valid refresh token must produce a new access_token."""
        from app.schemas.auth import RefreshTokenRequest
        req = RefreshTokenRequest(refresh_token=self.refresh_token)
        result = self.service.refresh_access_token(req)

        self.assertIn("access_token", result)
        self.assertEqual(result["token_type"], "bearer")
        self.assertNotIn("refresh_token", result)  # Refresh response has no refresh_token

    def test_new_access_token_is_valid(self):
        """The newly issued access token must pass verify_access_token."""
        from app.schemas.auth import RefreshTokenRequest
        req = RefreshTokenRequest(refresh_token=self.refresh_token)
        result = self.service.refresh_access_token(req)

        payload = verify_access_token(result["access_token"])
        self.assertIsNotNone(payload)
        self.assertEqual(payload["type"], "access")
        self.assertEqual(payload["user_id"], "USR-test-001")

    # ------------------------------------------------------------------
    # Security: access token cannot be used as refresh token
    # ------------------------------------------------------------------

    def test_access_token_rejected_as_refresh(self):
        """Sending an access token to /auth/refresh must raise 401."""
        from fastapi import HTTPException
        from app.schemas.auth import RefreshTokenRequest

        access_token = create_access_token(_TEST_PAYLOAD)
        req = RefreshTokenRequest(refresh_token=access_token)

        with self.assertRaises(HTTPException) as ctx:
            self.service.refresh_access_token(req)

        self.assertEqual(ctx.exception.status_code, 401)

    # ------------------------------------------------------------------
    # Invalid / expired tokens
    # ------------------------------------------------------------------

    def test_invalid_token_rejected(self):
        """A garbage string must raise 401."""
        from fastapi import HTTPException
        from app.schemas.auth import RefreshTokenRequest

        req = RefreshTokenRequest(refresh_token="garbage.token.value")
        with self.assertRaises(HTTPException) as ctx:
            self.service.refresh_access_token(req)
        self.assertEqual(ctx.exception.status_code, 401)

    def test_expired_refresh_token_rejected(self):
        """An expired refresh token must raise 401."""
        import jwt as pyjwt
        from datetime import datetime, timezone
        from fastapi import HTTPException
        from app.auth.jwt_handler import SECRET_KEY, ALGORITHM
        from app.schemas.auth import RefreshTokenRequest

        expired = pyjwt.encode(
            {**_TEST_PAYLOAD, "type": "refresh",
             "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            SECRET_KEY, algorithm=ALGORITHM
        )
        req = RefreshTokenRequest(refresh_token=expired)
        with self.assertRaises(HTTPException) as ctx:
            self.service.refresh_access_token(req)
        self.assertEqual(ctx.exception.status_code, 401)

    # ------------------------------------------------------------------
    # User validation
    # ------------------------------------------------------------------

    def test_nonexistent_user_rejected(self):
        """If the user no longer exists, refresh must raise 404."""
        from fastapi import HTTPException
        from app.schemas.auth import RefreshTokenRequest

        self.mock_repo.get_user_by_id.return_value = None
        req = RefreshTokenRequest(refresh_token=self.refresh_token)
        with self.assertRaises(HTTPException) as ctx:
            self.service.refresh_access_token(req)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_disabled_user_rejected(self):
        """If the user account is disabled, refresh must raise 403."""
        from fastapi import HTTPException
        from app.schemas.auth import RefreshTokenRequest

        self.mock_repo.get_user_by_id.return_value = _DISABLED_USER
        req = RefreshTokenRequest(refresh_token=self.refresh_token)
        with self.assertRaises(HTTPException) as ctx:
            self.service.refresh_access_token(req)
        self.assertEqual(ctx.exception.status_code, 403)

    # ------------------------------------------------------------------
    # No token values printed during refresh
    # ------------------------------------------------------------------

    def test_no_token_value_printed_during_refresh(self):
        """Token values must not be printed to stdout during refresh."""
        from app.schemas.auth import RefreshTokenRequest

        req = RefreshTokenRequest(refresh_token=self.refresh_token)
        _, output = _capture_stdout(self.service.refresh_access_token, req)
        self.assertNotIn("eyJ", output, "JWT value must not appear in stdout")


# ---------------------------------------------------------------------------
# Configuration Tests
# ---------------------------------------------------------------------------

class TestJWTConfiguration(unittest.TestCase):

    def test_secret_key_loaded_from_settings(self):
        """SECRET_KEY in jwt_handler must match the value in Settings."""
        from app.auth.jwt_handler import SECRET_KEY
        from app.config import get_settings
        self.assertEqual(SECRET_KEY, get_settings().JWT_SECRET_KEY)

    def test_algorithm_loaded_from_settings(self):
        from app.auth.jwt_handler import ALGORITHM
        from app.config import get_settings
        self.assertEqual(ALGORITHM, get_settings().JWT_ALGORITHM)

    def test_access_expire_loaded_from_settings(self):
        from app.auth.jwt_handler import ACCESS_TOKEN_EXPIRE_MINUTES
        from app.config import get_settings
        self.assertEqual(ACCESS_TOKEN_EXPIRE_MINUTES, get_settings().JWT_EXPIRE_MINUTES)

    def test_refresh_expire_loaded_from_settings(self):
        from app.auth.jwt_handler import REFRESH_TOKEN_EXPIRE_DAYS
        from app.config import get_settings
        self.assertEqual(REFRESH_TOKEN_EXPIRE_DAYS, get_settings().JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    def test_refresh_expire_days_in_settings(self):
        """JWT_REFRESH_TOKEN_EXPIRE_DAYS must exist in Settings with a positive value."""
        from app.config import get_settings
        val = get_settings().JWT_REFRESH_TOKEN_EXPIRE_DAYS
        self.assertIsInstance(val, int)
        self.assertGreater(val, 0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestJWTConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestJWTHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthServiceRefresh))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
