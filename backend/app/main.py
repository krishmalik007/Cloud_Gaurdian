"""
Cloud Guardian — Main FastAPI Application.

Entry point for the Cloud Guardian backend. Configures the app with:
- Lifespan-based startup/shutdown (replaces deprecated on_event)
- CORS middleware with configurable origins
- Rate limiting middleware
- JWT-protected API routes
- OpenSearch index template auto-creation
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.logger import setup_logger, logger
from app.services.opensearch_service import opensearch_service
from app.routes.auth_routes import router as auth_router
from app.routes.log_routes import router as log_router

# Load application settings
settings = get_settings()

# Reconfigure logger with settings
setup_logger(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

# OpenSearch index mapping for normalized logs
NORMALIZED_LOG_INDEX = "cloud-guardian-logs"
NORMALIZED_LOG_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "log_id": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "cloud_provider": {"type": "keyword"},
            "service": {"type": "keyword"},
            "event_name": {"type": "keyword"},
            "event_category": {"type": "keyword"},
            "user": {"type": "keyword"},
            "source_ip": {"type": "ip"},
            "destination_ip": {"type": "ip"},
            "resource": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "action": {"type": "keyword"},
            "status": {"type": "keyword"},
            "severity": {"type": "keyword"},
            "region": {"type": "keyword"},
            "risk_score": {"type": "integer"},
            "correlation_id": {"type": "keyword"},
            "raw_log": {"type": "object", "enabled": False},
        }
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown logic."""
    # ── Startup ──
    logger.info("=" * 50)
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting...")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Check OpenSearch connection
    if opensearch_service.ping():
        logger.info("OpenSearch is connected and ready.")

        # Create index template if it doesn't exist
        try:
            opensearch_service.create_index(
                index=NORMALIZED_LOG_INDEX,
                body=NORMALIZED_LOG_MAPPING,
            )
        except Exception as e:
            logger.warning(f"Could not create OpenSearch index: {e}")
    else:
        logger.warning("OpenSearch is not available. Logs will not be indexed.")

    # Check Kafka connectivity
    try:
        from app.kafka.kafka_service import kafka_producer
        if kafka_producer.health_check():
            logger.info("Kafka broker is connected and ready.")
        else:
            logger.warning("Kafka broker is not available.")
    except Exception as e:
        logger.warning(f"Kafka connection check skipped: {e}")

    logger.info("Backend is ready to receive requests.")
    logger.info("=" * 50)

    yield  # ← Application runs here

    # ── Shutdown ──
    logger.info("Shutting down Cloud Guardian...")
    try:
        from app.kafka.kafka_service import kafka_producer, kafka_consumer
        kafka_producer.flush()
        kafka_consumer.close()
    except Exception:
        pass
    logger.info("Cloud Guardian stopped.")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Cloud Guardian — AI-Powered Multi-Cloud Threat Detection & Correlation Platform.\n\n"
        "Ingests, parses, normalizes, and correlates security logs from AWS and Azure "
        "to detect multi-step attack patterns in real time."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(log_router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — welcome message."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """
    Deep health check — reports status of all backend services.
    """
    os_healthy = opensearch_service.ping()
    os_health = opensearch_service.cluster_health()

    kafka_healthy = False
    try:
        from app.kafka.kafka_service import kafka_producer
        kafka_healthy = kafka_producer.health_check()
    except Exception:
        pass

    overall = "healthy" if (os_healthy and kafka_healthy) else "degraded"

    return {
        "status": overall,
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "opensearch": {
                "status": "connected" if os_healthy else "disconnected",
                "cluster_status": os_health.get("status") if os_health else None,
            },
            "kafka": {
                "status": "connected" if kafka_healthy else "disconnected",
            },
        },
    }