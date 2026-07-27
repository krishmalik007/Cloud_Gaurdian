from fastapi import APIRouter, Depends, HTTPException

from app.auth.permissions import require_role
from app.logger import logger
from app.services.audit_service import audit_service

router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)


@router.get("/")
async def get_all_audit_logs(
    current_user=Depends(require_role("ADMIN"))
):
    """
    Retrieve all audit logs.
    Accessible only by ADMIN users.
    """
    try:

        logs = audit_service.get_all_logs()

        return {
            "success": True,
            "count": len(logs),
            "audit_logs": logs
        }

    except Exception as e:
        logger.exception("Failed to retrieve audit logs.")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{audit_id}")
async def get_audit_log(
    audit_id: str,
    current_user=Depends(require_role("ADMIN"))
):
    """
    Retrieve a specific audit log.
    Accessible only by ADMIN users.
    """
    try:

        log = audit_service.get_log(audit_id)

        if not log:
            raise HTTPException(
                status_code=404,
                detail="Audit log not found."
            )

        return log

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Failed to retrieve audit log.")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )