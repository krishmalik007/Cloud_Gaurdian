from fastapi import APIRouter, Depends, HTTPException

from app.auth.permissions import require_role
from app.logger import logger
from app.services.dashboard_service import dashboard_service

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
async def dashboard_summary(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve dashboard summary.
    Accessible by ADMIN and ANALYST.
    """
    try:
        return dashboard_service.get_summary()

    except Exception as e:
        logger.exception("Dashboard summary failed.")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/provider-stats")
async def provider_stats(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve cloud provider statistics.
    Accessible by ADMIN and ANALYST.
    """
    try:
        return dashboard_service.get_provider_stats()

    except Exception as e:
        logger.exception("Provider statistics failed.")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/risk-distribution")
async def risk_distribution(
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve incident risk distribution.
    Accessible by ADMIN and ANALYST.
    """
    try:
        return dashboard_service.get_risk_distribution()

    except Exception as e:
        logger.exception("Risk distribution failed.")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/recent-incidents")
async def recent_incidents(
    limit: int = 10,
    current_user=Depends(require_role("ADMIN", "ANALYST"))
):
    """
    Retrieve recent incidents.
    Accessible by ADMIN and ANALYST.
    """
    try:
        return dashboard_service.get_recent_incidents(limit)

    except Exception as e:
        logger.exception("Recent incidents failed.")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )