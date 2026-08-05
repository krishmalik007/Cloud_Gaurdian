from pydantic import BaseModel


class IOCResponse(BaseModel):
    ioc_type: str
    value: str
    malicious: bool
    severity: str
    tags: list[str]