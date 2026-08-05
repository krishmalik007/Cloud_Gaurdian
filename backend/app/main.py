from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.logger import logger
from app.services.opensearch_service import opensearch_service

# Import Routers
from app.routes.health import router as health_router
from app.routes.logs import router as logs_router
from app.routes.incidents import router as incidents_router
from app.routes.dashboard import router as dashboard_router
from app.routes.auth import router as auth_router
from app.routes.audit import router as audit_router
from app.routes.users import router as users_router
from app.routes.threat import router as threat_router
from app.routes.iocs import router as iocs_router

# Load application settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Cloud Guardian - Cloud Security Log Correlation Platform"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(logs_router)
app.include_router(incidents_router)
app.include_router(dashboard_router)
app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(users_router)
app.include_router(threat_router)
app.include_router(iocs_router)


@app.on_event("startup")
async def startup_event():
    """
    Application Startup Event
    """

    logger.info("=" * 60)
    logger.info(f"{settings.APP_NAME} Started Successfully")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("Backend is ready to receive requests.")

    # Verify OpenSearch Connection
    if opensearch_service.ping():
        logger.info("OpenSearch is connected and ready.")
    else:
        logger.error("OpenSearch connection failed.")

    logger.info("=" * 60)


@app.get("/", tags=["Root"])
async def root():
    """
    Root Endpoint
    """

    logger.info("Root endpoint accessed.")

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
        "documentation": "/docs",
        "health": "/health/",
        "log_ingestion": "/logs/"
    }