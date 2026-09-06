from typing import Literal
from pydantic import BaseModel


class UserRoleUpdate(BaseModel):
    role: Literal["ADMIN", "ANALYST", "VIEWER"]


class UserStatusUpdate(BaseModel):
    enabled: bool