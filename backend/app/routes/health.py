from fastapi import APIRouter
from app.services.opensearch_service import opensearch_service
from app.config import get_settings

settings = get_settings()

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
async def health_check():

    opensearch_status = (
        "connected"
        if opensearch_service.ping()
        else "disconnected"
    )

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "opensearch": opensearch_status
    }