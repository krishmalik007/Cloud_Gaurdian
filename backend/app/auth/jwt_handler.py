from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import get_settings

# All JWT parameters are read from the .env / Settings object.
# Nothing is hardcoded here — secrets must never appear in source code.
_settings = get_settings()

SECRET_KEY: str = _settings.JWT_SECRET_KEY
ALGORITHM: str = _settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = _settings.JWT_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS: int = _settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS


# ==========================================
# Create Access Token
# ==========================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    """
    Generate a JWT Access Token.

    Embeds ``"type": "access"`` so the backend can distinguish it from
    a refresh token.  Access tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES
    (configured via JWT_EXPIRE_MINUTES in .env).
    """

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + (
            expires_delta
            if expires_delta
            else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
    )

    to_encode.update({
        "exp": expire,
        "type": "access"
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================================
# Create Refresh Token
# ==========================================

def create_refresh_token(data: dict):
    """
    Generate a JWT Refresh Token.

    Embeds ``"type": "refresh"`` so it cannot be accepted by the
    ``verify_access_token`` guard on protected endpoints.
    Refresh tokens expire after REFRESH_TOKEN_EXPIRE_DAYS
    (configured via JWT_REFRESH_TOKEN_EXPIRE_DAYS in .env).
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================================
# Verify Token (base — decodes any token)
# ==========================================

def verify_token(token: str):
    """
    Decode and verify the JWT signature and expiry.
    Returns the payload dict on success, None on any error.
    Errors are swallowed intentionally — callers use the None return
    to raise a generic 401 so token internals are not leaked.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except InvalidTokenError:
        return None


# ==========================================
# Verify Access Token
# ==========================================

def verify_access_token(token: str):
    """
    Verify signature, expiry, AND that the token type is "access".
    A refresh token will return None here, ensuring it cannot be used
    as an access token on protected endpoints.
    """
    payload = verify_token(token)

    if not payload:
        return None

    if payload.get("type") != "access":
        return None

    return payload


# ==========================================
# Verify Refresh Token
# ==========================================

def verify_refresh_token(token: str):
    """
    Verify signature, expiry, AND that the token type is "refresh".
    An access token will return None here, ensuring the /auth/refresh
    endpoint cannot be abused with a valid access token.
    """
    payload = verify_token(token)

    if not payload:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload