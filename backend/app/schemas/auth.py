from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# -----------------------------
# Register Request
# -----------------------------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    role: str = "ANALYST"


# -----------------------------
# Login Request
# -----------------------------
class UserLogin(BaseModel):
    email: str
    password: str


# -----------------------------
# Token Response
# -----------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -----------------------------
# User Response
# -----------------------------
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    created_at: datetime


# -----------------------------
# JWT Payload
# -----------------------------
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None