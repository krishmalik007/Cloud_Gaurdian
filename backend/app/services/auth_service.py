from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)
from app.auth.password import hash_password, verify_password
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest
)
from app.services.audit_service import audit_service
from app.storage.user_repository import UserRepository


class AuthService:

    def __init__(self):
        self.repository = UserRepository()

    # ------------------------------------
    # Register User
    # ------------------------------------
    def register_user(self, user: UserRegister):

        existing = self.repository.get_user_by_email(user.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )

        user_id = f"USR-{int(datetime.now().timestamp())}"

        new_user = {
            "user_id": user_id,
            "username": user.username,
            "email": user.email,
            "password": hash_password(user.password),
            "role": user.role,
            "enabled": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        self.repository.create_user(new_user)

        audit_service.create_log(
            user_id=user_id,
            username=user.username,
            action="REGISTER",
            resource="AUTH",
            status="SUCCESS"
        )

        return {
            "message": "User registered successfully.",
            "user_id": user_id
        }

    # ------------------------------------
    # Login User
    # ------------------------------------
    def login_user(self, credentials: UserLogin):

        user = self.repository.get_user_by_email(
            credentials.email
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not verify_password(
            credentials.password,
            user["password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Prevent disabled users from logging in
        if not user.get("enabled", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled."
            )

        payload = {
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user["role"]
        }

        access_token = create_access_token(payload)

        refresh_token = create_refresh_token(payload)

        audit_service.create_log(
            user_id=user["user_id"],
            username=user["username"],
            action="LOGIN",
            resource="AUTH",
            status="SUCCESS"
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    # ------------------------------------
    # Refresh Access Token
    # ------------------------------------
    def refresh_access_token(
        self,
        request: RefreshTokenRequest
    ):

        payload = verify_refresh_token(
            request.refresh_token
        )

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        user = self.repository.get_user_by_id(
            payload["user_id"]
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        if not user.get("enabled", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled."
            )

        access_token = create_access_token(
            {
                "user_id": user["user_id"],
                "email": user["email"],
                "role": user["role"]
            }
        )

        audit_service.create_log(
            user_id=user["user_id"],
            username=user["username"],
            action="REFRESH_TOKEN",
            resource="AUTH",
            status="SUCCESS"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    # ------------------------------------
    # Get User
    # ------------------------------------
    def get_user(self, user_id: str):

        user = self.repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        user.pop("password", None)

        return user


auth_service = AuthService()