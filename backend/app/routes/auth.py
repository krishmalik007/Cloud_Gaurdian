from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.schemas.auth import (
    UserRegister,
    UserLogin,
)
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

service = AuthService()


@router.post("/register")
def register(user: UserRegister):
    return service.register_user(user)


@router.post("/login")
def login(credentials: UserLogin):
    return service.login_user(credentials)


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    current_user.pop("password", None)
    return current_user