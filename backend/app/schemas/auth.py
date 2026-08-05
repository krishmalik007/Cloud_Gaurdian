from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ------------------------------------
# Register Request
# ------------------------------------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    role: str = "ANALYST"


# ------------------------------------
# Login Request
# ------------------------------------
class UserLogin(BaseModel):
    email: str
    password: str


# ------------------------------------
# Refresh Token Request
# ------------------------------------
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ------------------------------------
# Token Response
# ------------------------------------
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ------------------------------------
# User Response
# ------------------------------------
class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    enabled: bool
    created_at: datetime


# ------------------------------------
# JWT Payload
# ------------------------------------
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    token_type: Optional[str] = None