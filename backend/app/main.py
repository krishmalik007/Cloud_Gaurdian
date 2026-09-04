from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.logger import logger
from app.services.opensearch_service import opensearch_service
from app.services.aws_sqs_consumer import sqs_consumer
from app.services.websocket_manager import ws_manager
from app.auth.jwt_handler import verify_access_token

import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect

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

    # Initialize WebSocket manager with the main event loop
    try:
        ws_manager.set_loop(asyncio.get_running_loop())
        logger.info("WebSocket manager loop initialized.")
    except RuntimeError:
        logger.warning("Could not get running event loop for WebSocket manager.")

    # Verify OpenSearch Connection
    if opensearch_service.ping():
        logger.info("OpenSearch is connected and ready.")
    else:
        logger.error("OpenSearch connection failed.")

    # Start AWS SQS consumer background thread
    sqs_consumer.start()

    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application Shutdown Event
    """

    logger.info("=" * 60)
    logger.info(f"{settings.APP_NAME} is shutting down...")

    # Stop AWS SQS consumer gracefully
    sqs_consumer.stop()

    logger.info(f"{settings.APP_NAME} shutdown complete.")
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


@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates.
    Authentication: The client must send a JSON payload with a valid
    'token' (JWT access token) as the very first message.
    """
    await websocket.accept()

    try:
        # Wait for the first message to authenticate
        auth_message = await websocket.receive_text()

        try:
            data = json.loads(auth_message)
        except json.JSONDecodeError:
            logger.warning("WebSocket authentication failed: Invalid JSON payload.")
            await websocket.close(code=1008)
            return

        token = data.get("token")
        if not token:
            logger.warning("WebSocket authentication failed: No token provided.")
            await websocket.close(code=1008)
            return

        payload = verify_access_token(token)
        if not payload:
            logger.warning("WebSocket authentication failed: Invalid or expired token.")
            await websocket.close(code=1008)
            return

        role = payload.get("role")
        if role not in ["ADMIN", "ANALYST"]:
            logger.warning(f"WebSocket authentication failed: Insufficient role ({role}).")
            await websocket.close(code=1008)
            return

        # Authenticated successfully
        ws_manager.add_connection(websocket)
        await websocket.send_json({"status": "authenticated"})

        # Keep connection open and wait for client to disconnect or send keepalives
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)