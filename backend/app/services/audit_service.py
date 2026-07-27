from datetime import datetime, timezone

from app.storage.audit_repository import AuditRepository



class AuditService:

    def __init__(self):
        self.repository = AuditRepository()

    def create_log(
        self,
        user_id: str,
        username: str,
        action: str,
        resource: str,
        status: str,
        ip_address: str = "127.0.0.1"
    ):
        """
        Create and store an audit log.
        """

        audit_log = {
            "audit_id": f"AUD-{int(datetime.now().timestamp())}",
            "user_id": user_id,
            "username": username,
            "action": action,
            "resource": resource,
            "status": status,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.repository.create_log(audit_log)

        return audit_log

    def get_all_logs(self):
        """
        Retrieve all audit logs.
        """
        return self.repository.get_all_logs()

    def get_log(self, audit_id: str):
        """
        Retrieve a single audit log.
        """
        return self.repository.get_log(audit_id)


audit_service = AuditService()