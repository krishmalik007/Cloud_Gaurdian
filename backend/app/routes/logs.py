from fastapi import APIRouter, HTTPException

from app.logger import logger
from app.services.log_processor import log_processor

router = APIRouter(
    prefix="/logs",
    tags=["Logs"]
)


@router.post("/")
async def process_cloud_log(raw_log: dict):
    """
    Process an incoming cloud log.

    Supported Providers:
    - AWS
    - Azure
    - GCP
    """

    try:

        logger.info("Received new cloud log.")

        incident = log_processor.process_log(raw_log)

        return {
            "success": True,
            "message": "Log processed successfully.",
            "incident": incident
        }

    except Exception as e:

        logger.exception("Error while processing cloud log.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )