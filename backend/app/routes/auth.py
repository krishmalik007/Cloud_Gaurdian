from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    RefreshTokenRequest,
    RefreshTokenResponse
)
from app.services.auth_service import auth_service

from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiter — in-memory storage, no Redis required
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ------------------------------------
# Register
# ------------------------------------
@router.post("/register")
@limiter.limit("5/minute")
def register(request: Request, user: UserRegister):
    return auth_service.register_user(user)


# ------------------------------------
# Login
# ------------------------------------
@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, credentials: UserLogin):
    return auth_service.login_user(credentials)


# ------------------------------------
# Refresh Access Token
# ------------------------------------
@router.post("/refresh", response_model=RefreshTokenResponse)
@limiter.limit("30/minute")
def refresh_token(request: Request, token_request: RefreshTokenRequest):
    return auth_service.refresh_access_token(token_request)


# ------------------------------------
# Logout User
# ------------------------------------
@router.post("/logout")
@limiter.limit("10/minute")
def logout(request: Request, current_user=Depends(get_current_user)):
    session_id = current_user.get("session_id")
    if session_id:
        auth_service.logout_user(session_id)
    return {"message": "Logged out successfully"}


# ------------------------------------
# Current Logged-in User
# ------------------------------------
@router.get("/me")
def me(current_user=Depends(get_current_user)):
    current_user.pop("password", None)
    return current_user