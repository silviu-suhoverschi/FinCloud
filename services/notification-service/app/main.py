"""
Notification Service - Event-driven notification service for FinCloud
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import structlog

from app.core.config import settings
from app.core.redis import redis_manager
from app.api.v1.endpoints import notifications, preferences, webhooks
from app.services.event_queue import EventQueueService
from app.services.email_service import EmailService
from app.services.telegram_service import TelegramService
from app.services.webhook_service import WebhookService
from app.services.template_service import TemplateService
from app.services.preference_service import PreferenceService

logger = structlog.get_logger()

# Global event queue processor
event_queue_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management"""
    global event_queue_task

    # Startup
    logger.info("notification_service_starting")

    # Connect to Redis
    await redis_manager.connect()

    # Initialize services
    redis_client = redis_manager.get_client()
    email_service = EmailService()
    telegram_service = TelegramService()
    webhook_service = WebhookService()
    template_service = TemplateService()
    preference_service = PreferenceService(redis_client)

    event_queue = EventQueueService(
        redis_client=redis_client,
        email_service=email_service,
        telegram_service=telegram_service,
        webhook_service=webhook_service,
        template_service=template_service,
        preference_service=preference_service,
    )

    # Start event queue processor in background
    event_queue_task = asyncio.create_task(event_queue.start_processing())
    logger.info("event_queue_processor_started")

    # Store in app state for access in endpoints
    app.state.event_queue = event_queue

    logger.info("notification_service_started")

    yield

    # Shutdown
    logger.info("notification_service_stopping")

    # Stop event queue processor
    if event_queue_task:
        await event_queue.stop_processing()
        event_queue_task.cancel()
        try:
            await event_queue_task
        except asyncio.CancelledError:
            pass

    # Disconnect from Redis
    await redis_manager.disconnect()

    logger.info("notification_service_stopped")


app = FastAPI(
    title="FinCloud Notification Service",
    description="Event-driven notification service for FinCloud",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_client = redis_manager.get_client()
        await redis_client.ping()

        # Check event queue
        queue_length = 0
        if hasattr(app.state, "event_queue"):
            queue_length = await app.state.event_queue.get_queue_length()

        return {
            "status": "healthy",
            "redis": "connected",
            "queue_length": queue_length,
            "email_configured": EmailService().is_configured(),
            "telegram_configured": TelegramService().is_configured(),
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
        }


@app.get("/info")
async def service_info():
    """Service information"""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "email": EmailService().is_configured(),
            "telegram": TelegramService().is_configured(),
            "webhooks": True,
            "event_queue": True,
        },
    }


# Include API routers
app.include_router(
    notifications.router,
    prefix="/api/v1/notifications",
    tags=["notifications"],
)

app.include_router(
    preferences.router,
    prefix="/api/v1/preferences",
    tags=["preferences"],
)

app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["webhooks"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
