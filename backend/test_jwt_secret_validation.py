"""
Tests for JWT_SECRET_KEY length validation in app/config.py.

Each test constructs Settings with fully controlled values so the live
backend/.env is never read.  We use Settings(_env_file=None, **env) to
suppress pydantic-settings file loading and pass all values explicitly.
"""

import pytest
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# Minimal valid base values — all required fields, secret exactly 32 chars
# ---------------------------------------------------------------------------
VALID_KWARGS = dict(
    KAFKA_BOOTSTRAP_SERVERS="localhost:9092",
    KAFKA_TOPIC="cloud_logs",
    OPENSEARCH_HOST="localhost",
    OPENSEARCH_USERNAME="admin",
    OPENSEARCH_PASSWORD="admin",
    # Exactly 32 chars — the minimum accepted boundary
    JWT_SECRET_KEY="a" * 32,
)


def make_settings(**overrides):
    """
    Instantiate Settings from explicit keyword arguments only.
    _env_file=None suppresses all .env file loading so the live
    backend/.env never contaminates test values.
    """
    from app.config import Settings

    kwargs = {**VALID_KWARGS, **overrides}
    return Settings(_env_file=None, **kwargs)


# ===========================================================================
# 1. Valid secrets — must succeed
# ===========================================================================

class TestJwtSecretValid:

    def test_exactly_32_characters_succeeds(self):
        """Boundary: exactly 32 chars is the minimum accepted value."""
        s = make_settings(JWT_SECRET_KEY="x" * 32)
        assert len(s.JWT_SECRET_KEY) == 32

    def test_64_character_hex_secret_succeeds(self):
        """A real 256-bit hex secret (output of secrets.token_hex(32))."""
        strong = "63ef831fdee871e92ef550a535cf0894b7e63a46d567c829080fa9a0368bd9ad"
        assert len(strong) == 64
        s = make_settings(JWT_SECRET_KEY=strong)
        assert s.JWT_SECRET_KEY == strong

    def test_33_characters_succeeds(self):
        """One character above the minimum."""
        s = make_settings(JWT_SECRET_KEY="y" * 33)
        assert len(s.JWT_SECRET_KEY) == 33

    def test_secret_value_is_not_altered(self):
        """Validator must return the original value unchanged."""
        secret = "z" * 48
        s = make_settings(JWT_SECRET_KEY=secret)
        assert s.JWT_SECRET_KEY == secret


# ===========================================================================
# 2. Invalid secrets — must raise ValidationError at startup
# ===========================================================================

class TestJwtSecretInvalid:

    def _assert_jwt_error(self, **overrides):
        with pytest.raises(ValidationError) as exc_info:
            make_settings(**overrides)
        errors = exc_info.value.errors()
        jwt_errors = [e for e in errors if "JWT_SECRET_KEY" in str(e.get("loc", ""))]
        assert jwt_errors, (
            f"Expected a ValidationError on JWT_SECRET_KEY but got: {errors}"
        )
        return exc_info

    def test_31_characters_fails(self):
        """One character below the minimum must be rejected."""
        self._assert_jwt_error(JWT_SECRET_KEY="a" * 31)

    def test_empty_string_fails(self):
        """An empty secret must be rejected."""
        self._assert_jwt_error(JWT_SECRET_KEY="")

    def test_single_character_fails(self):
        """A trivially short secret must be rejected."""
        self._assert_jwt_error(JWT_SECRET_KEY="s")

    def test_placeholder_value_fails(self):
        """The 15-char placeholder your-secret-key must be rejected."""
        self._assert_jwt_error(JWT_SECRET_KEY="your-secret-key")

    def test_error_message_contains_minimum_length(self):
        """The validation error message must state the required length."""
        exc_info = self._assert_jwt_error(JWT_SECRET_KEY="too_short")
        # Check only the validator message, not Pydantic input_value repr
        errors = exc_info.value.errors()
        jwt_error = next(e for e in errors if "JWT_SECRET_KEY" in str(e.get("loc", "")))
        msg = jwt_error.get("msg", "")
        assert "32" in msg

    def test_error_message_contains_generation_guidance(self):
        """The validator must tell the operator how to generate a strong key."""
        exc_info = self._assert_jwt_error(JWT_SECRET_KEY="too_short")
        errors = exc_info.value.errors()
        jwt_error = next(e for e in errors if "JWT_SECRET_KEY" in str(e.get("loc", "")))
        msg = jwt_error.get("msg", "")
        assert "secrets.token_hex" in msg


# ===========================================================================
# 3. Missing JWT_SECRET_KEY — field is required, must fail at startup
# ===========================================================================

class TestJwtSecretMissing:

    def test_missing_jwt_secret_key_fails(self):
        """
        JWT_SECRET_KEY has no default (Field(...)). Omitting it must raise
        a ValidationError listing JWT_SECRET_KEY as a missing required field.
        """
        from app.config import Settings

        with pytest.raises(ValidationError) as exc_info:
            Settings(
                _env_file=None,
                KAFKA_BOOTSTRAP_SERVERS="localhost:9092",
                KAFKA_TOPIC="cloud_logs",
                OPENSEARCH_HOST="localhost",
                OPENSEARCH_USERNAME="admin",
                OPENSEARCH_PASSWORD="admin",
                # JWT_SECRET_KEY intentionally omitted
            )

        errors = exc_info.value.errors()
        jwt_errors = [e for e in errors if "JWT_SECRET_KEY" in str(e.get("loc", ""))]
        assert jwt_errors, (
            f"Expected missing-field error for JWT_SECRET_KEY but got: {errors}"
        )


# ===========================================================================
# 4. Regression — existing settings and defaults load correctly
# ===========================================================================

class TestSettingsRegression:

    def test_all_default_optional_fields_load(self):
        """Optional fields resolve to correct defaults when not supplied."""
        s = make_settings()
        assert s.JWT_ALGORITHM == "HS256"
        assert s.JWT_EXPIRE_MINUTES == 30
        assert s.JWT_REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert s.DEBUG is False
        assert s.OPENSEARCH_USE_SSL is False
        # Optional AWS fields must be None when not supplied and .env is suppressed
        assert s.AWS_ACCESS_KEY_ID is None
        assert s.AWS_SECRET_ACCESS_KEY is None
        assert s.AWS_SQS_QUEUE_URL is None

    def test_jwt_handler_reads_from_settings(self):
        """
        Verify the live secret loaded by jwt_handler from the real .env
        already meets the 32-character minimum.
        """
        from app.auth.jwt_handler import SECRET_KEY
        assert isinstance(SECRET_KEY, str)
        assert len(SECRET_KEY) >= 32, (
            "The live JWT_SECRET_KEY from backend/.env is shorter than 32 characters. "
            "Update it: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
