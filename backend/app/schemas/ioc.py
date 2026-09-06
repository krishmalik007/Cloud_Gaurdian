from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class IOCCreate(BaseModel):
    type: Literal["IP", "DOMAIN", "USERNAME"] = Field(..., examples=["IP", "DOMAIN", "USERNAME"])
    value: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    source: str = "MANUAL"
    description: Optional[str] = None
    enabled: bool = True


class IOCUpdate(BaseModel):
    severity: Optional[Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class IOCResponse(BaseModel):
    ioc_id: str
    type: str
    value: str
    severity: str
    source: str
    description: Optional[str]
    enabled: bool
    created_at: datetime