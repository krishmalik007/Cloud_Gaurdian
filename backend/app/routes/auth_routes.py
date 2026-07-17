"""
Cloud Guardian — Authentication Routes.

REST endpoints for user registration, login, and profile access.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_handler import (
    create_access_token,
    get_current_user,
    require_admin,
    user_store,
)
from app.config import get_settings
from app.logger import logger
from app.models.user_models import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(request: UserRegisterRequest, admin: dict = Depends(require_admin)):
    """
    Register a new user account. Requires admin privileges.
    """
    try:
        user = user_store.create_user(
            username=request.username,
            password=request.password,
            role=request.role,
        )
        logger.info(f"New user registered: {request.username} by admin: {admin['username']}")
        return UserResponse(**user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get JWT token",
)
async def login(request: UserLoginRequest):
    """
    Authenticate with username and password. Returns a JWT access token.
    """
    if not user_store.verify_password(request.username, request.password):
        logger.warning(f"Failed login attempt for user: {request.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    settings = get_settings()
    user = user_store.get_user(request.username)

    token = create_access_token(data={"sub": request.username, "role": user["role"]})

    logger.info(f"User logged in: {request.username}")
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return UserResponse(username=current_user["username"], role=current_user["role"])
