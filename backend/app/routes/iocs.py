from fastapi import APIRouter, Depends, HTTPException

from app.auth.permissions import require_role
from app.logger import logger
from app.schemas.ioc import IOCCreate, IOCUpdate
from app.services.audit_service import audit_service
from app.services.ioc_service import ioc_service

router = APIRouter(
    prefix="/iocs",
    tags=["IOC Management"]
)


# --------------------------------------------------
# Create IOC
# --------------------------------------------------
@router.post("/")
async def create_ioc(
    ioc: IOCCreate,
    current_user=Depends(require_role("ADMIN"))
):
    """
    Create a new Indicator of Compromise.
    """

    try:

        created = ioc_service.create_ioc(
            ioc.model_dump()
        )

        audit_service.create_log(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="CREATE_IOC",
            resource=created["ioc_id"],
            status="SUCCESS"
        )

        return created

    except Exception as e:

        logger.exception("IOC creation failed.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Get All IOCs
# --------------------------------------------------
@router.get("/")
async def get_all_iocs(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve all Indicators of Compromise.
    """

    return ioc_service.get_all_iocs()


# --------------------------------------------------
# Get IOC
# --------------------------------------------------
@router.get("/{ioc_id}")
async def get_ioc(
    ioc_id: str,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve a single IOC.
    """

    return ioc_service.get_ioc(ioc_id)


# --------------------------------------------------
# Update IOC
# --------------------------------------------------
@router.put("/{ioc_id}")
async def update_ioc(
    ioc_id: str,
    updates: IOCUpdate,
    current_user=Depends(require_role("ADMIN"))
):
    """
    Update an IOC.
    """

    updated = ioc_service.update_ioc(
        ioc_id,
        updates.model_dump(exclude_none=True)
    )

    audit_service.create_log(
        user_id=current_user["user_id"],
        username=current_user["username"],
        action="UPDATE_IOC",
        resource=ioc_id,
        status="SUCCESS"
    )

    return updated


# --------------------------------------------------
# Delete IOC
# --------------------------------------------------
@router.delete("/{ioc_id}")
async def delete_ioc(
    ioc_id: str,
    current_user=Depends(require_role("ADMIN"))
):
    """
    Delete an IOC.
    """

    result = ioc_service.delete_ioc(ioc_id)

    audit_service.create_log(
        user_id=current_user["user_id"],
        username=current_user["username"],
        action="DELETE_IOC",
        resource=ioc_id,
        status="SUCCESS"
    )

    return result