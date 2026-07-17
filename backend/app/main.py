from fastapi import FastAPI

from app.config import get_settings
from app.logger import logger
from app.services.opensearch_service import opensearch_service

# Load application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cloud Guardian - Cloud Security Log Correlation Platform"
)


@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info(f"{settings.APP_NAME} Started Successfully")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("Backend is ready to receive requests.")

    # Check OpenSearch connection
    if opensearch_service.ping():
        logger.info("OpenSearch is connected and ready.")
    else:
        logger.error("OpenSearch connection failed.")

    logger.info("=" * 50)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")

    return {
        "message": "Welcome to Cloud Guardian API"
    }


@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed.")

    return {
        "status": "healthy",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }