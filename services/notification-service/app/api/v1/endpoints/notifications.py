"""
Notification endpoints
"""

import uuid
from datetime import datetime
from typing import Any

import redis.asyncio as redis
import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.redis import get_redis
from app.schemas.event import EventType, NotificationEvent
from app.schemas.notification import NotificationCreate
from app.services.email_service import EmailService
from app.services.event_queue import EventQueueService
from app.services.preference_service import PreferenceService
from app.services.telegram_service import TelegramService
from app.services.template_service import TemplateService
from app.services.webhook_service import WebhookService

logger = structlog.get_logger()

router = APIRouter()


async def get_event_queue_service(redis_client: redis.Redis = Depends(get_redis)):
    """Dependency to get event queue service"""
    email_service = EmailService()
    telegram_service = TelegramService()
    webhook_service = WebhookService()
    template_service = TemplateService()
    preference_service = PreferenceService(redis_client)

    return EventQueueService(
        redis_client=redis_client,
        email_service=email_service,
        telegram_service=telegram_service,
        webhook_service=webhook_service,
        template_service=template_service,
        preference_service=preference_service,
    )


@router.post("/send", response_model=dict[str, Any], status_code=status.HTTP_202_ACCEPTED)
async def send_notification(
    notification: NotificationCreate,
    event_queue: EventQueueService = Depends(get_event_queue_service),
):
    """
    Send a notification (enqueues event for processing)
    """
    try:
        # Map notification type to event type
        event_type_mapping = {
            "budget_alert": EventType.BUDGET_THRESHOLD_EXCEEDED,
            "transaction_created": EventType.TRANSACTION_CREATED,
            "portfolio_alert": EventType.PORTFOLIO_VALUE_CHANGED,
            "price_alert": EventType.PRICE_ALERT,
            "system_alert": EventType.SYSTEM_UPDATE,
        }

        event_type = event_type_mapping.get(
            notification.notification_type, EventType.USER_ACTION_REQUIRED
        )

        # Create event
        event = NotificationEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=notification.user_id,
            timestamp=datetime.utcnow(),
            data={
                "subject": notification.subject,
                "message": notification.message,
                **(notification.data or {}),
            },
            priority=notification.priority,
        )

        # Enqueue event
        success = await event_queue.enqueue_event(event)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enqueue notification",
            )

        return {
            "status": "accepted",
            "event_id": event.event_id,
            "message": "Notification queued for processing",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("send_notification_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}",
        ) from e


@router.post("/event", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_event(
    event: NotificationEvent,
    event_queue: EventQueueService = Depends(get_event_queue_service),
):
    """
    Enqueue a notification event
    """
    try:
        success = await event_queue.enqueue_event(event)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to enqueue event",
            )

        return {
            "status": "accepted",
            "event_id": event.event_id,
            "message": "Event queued for processing",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("enqueue_event_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue event: {str(e)}",
        ) from e


@router.get("/queue/stats")
async def get_queue_stats(
    event_queue: EventQueueService = Depends(get_event_queue_service),
):
    """
    Get queue statistics
    """
    try:
        queue_length = await event_queue.get_queue_length()

        return {
            "queue_length": queue_length,
            "processing": event_queue.processing,
        }

    except Exception as e:
        logger.error("get_queue_stats_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get queue stats: {str(e)}",
        ) from e
