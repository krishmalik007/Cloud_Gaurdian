from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest
)
from app.services.auth_service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ------------------------------------
# Register
# ------------------------------------
@router.post("/register")
def register(user: UserRegister):
    return auth_service.register_user(user)


# ------------------------------------
# Login
# ------------------------------------
@router.post("/login")
def login(credentials: UserLogin):
    return auth_service.login_user(credentials)


# ------------------------------------
# Refresh Access Token
# ------------------------------------
@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    return auth_service.refresh_access_token(request)


# ------------------------------------
# Current Logged-in User
# ------------------------------------
@router.get("/me")
def me(current_user=Depends(get_current_user)):
    current_user.pop("password", None)
    return current_user