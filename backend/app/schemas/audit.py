from pydantic import BaseModel


class AuditLog(BaseModel):
    audit_id: str
    user_id: str
    username: str
    action: str
    resource: str
    status: str
    ip_address: str
    timestamp: str
    