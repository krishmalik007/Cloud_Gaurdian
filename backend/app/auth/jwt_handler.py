from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError

# ==========================================
# JWT Configuration
# ==========================================

SECRET_KEY = "cloudguardian-super-secret-key-change-in-production"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ==========================================
# Create Access Token
# ==========================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    """
    Generate JWT Access Token.
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
    Generate JWT Refresh Token.
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
# Verify Token
# ==========================================

def verify_token(token: str):

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

    payload = verify_token(token)

    if not payload:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload