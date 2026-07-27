from pydantic import BaseModel


class UserRoleUpdate(BaseModel):
    role: str


class UserStatusUpdate(BaseModel):
    enabled: bool