from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IOCCreate(BaseModel):
    type: str = Field(..., examples=["IP", "DOMAIN", "USERNAME"])
    value: str
    severity: str = "MEDIUM"
    source: str = "MANUAL"
    description: Optional[str] = None
    enabled: bool = True


class IOCUpdate(BaseModel):
    severity: Optional[str] = None
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