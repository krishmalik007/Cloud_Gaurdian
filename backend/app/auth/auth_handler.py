"""
Cloud Guardian — Authentication Module.

Provides JWT-based authentication with an in-memory user store for development.
Includes password hashing via bcrypt and token generation/validation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from app.config import get_settings
from app.logger import logger

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security scheme
security = HTTPBearer()


class InMemoryUserStore:
    """
    Simple in-memory user store for development/demo purposes.
    Replace with a database-backed solution for production.
    """

    def __init__(self):
        self._users: dict[str, dict[str, str]] = {}

        # Create a default admin user
        self._users["admin"] = {
            "username": "admin",
            "password_hash": pwd_context.hash("Admin@1234"),
            "role": "admin",
        }
        logger.info("In-memory user store initialized with default admin user.")

    def get_user(self, username: str) -> dict[str, str] | None:
        """Get a user by username."""
        return self._users.get(username)

    def create_user(self, username: str, password: str, role: str = "analyst") -> dict[str, str]:
        """Create a new user with hashed password."""
        if username in self._users:
            raise ValueError(f"User '{username}' already exists")

        self._users[username] = {
            "username": username,
            "password_hash": pwd_context.hash(password),
            "role": role,
        }
        logger.info(f"User created: {username} (role: {role})")
        return {"username": username, "role": role}

    def verify_password(self, username: str, password: str) -> bool:
        """Verify a user's password."""
        user = self.get_user(username)
        if not user:
            return False
        return pwd_context.verify(password, user["password_hash"])


# Singleton user store
user_store = InMemoryUserStore()


def create_access_token(data: dict[str, Any]) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload to encode (must include 'sub' for the username).

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict[str, str]:
    """
    FastAPI dependency that extracts and validates the current user from the JWT token.

    Returns:
        User dictionary with 'username' and 'role'.
    """
    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )

    user = user_store.get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {"username": user["username"], "role": user["role"]}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """FastAPI dependency that ensures the current user is an admin."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
