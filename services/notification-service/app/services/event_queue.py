"""
Event queue service for processing notification events
"""
import json
import asyncio
from typing import Optional, Dict, Any
import structlog
import redis.asyncio as redis

from app.core.config import settings
from app.schemas.event import NotificationEvent, EventType
from app.schemas.notification import NotificationType, NotificationChannel
from app.services.email_service import EmailService
from app.services.telegram_service import TelegramService
from app.services.webhook_service import WebhookService
from app.services.template_service import TemplateService
from app.services.preference_service import PreferenceService

logger = structlog.get_logger()


class EventQueueService:
    """Event queue processing service"""

    def __init__(
        self,
        redis_client: redis.Redis,
        email_service: EmailService,
        telegram_service: TelegramService,
        webhook_service: WebhookService,
        template_service: TemplateService,
        preference_service: PreferenceService,
    ):
        self.redis = redis_client
        self.email_service = email_service
        self.telegram_service = telegram_service
        self.webhook_service = webhook_service
        self.template_service = template_service
        self.preference_service = preference_service
        self.queue_name = settings.EVENT_QUEUE_NAME
        self.processing = False

    async def enqueue_event(self, event: NotificationEvent) -> bool:
        """
        Add event to the queue

        Args:
            event: Notification event

        Returns:
            True if event was enqueued successfully
        """
        try:
            await self.redis.rpush(
                self.queue_name,
                event.model_dump_json(),
            )
            logger.info(
                "event_enqueued",
                event_id=event.event_id,
                event_type=event.event_type,
                user_id=event.user_id,
            )
            return True

        except Exception as e:
            logger.error(
                "enqueue_event_failed",
                event_id=event.event_id,
                error=str(e),
            )
            return False

    async def dequeue_event(self) -> Optional[NotificationEvent]:
        """
        Get next event from the queue

        Returns:
            NotificationEvent or None if queue is empty
        """
        try:
            data = await self.redis.lpop(self.queue_name)
            if data:
                event_dict = json.loads(data)
                return NotificationEvent(**event_dict)
            return None

        except Exception as e:
            logger.error("dequeue_event_failed", error=str(e))
            return None

    async def process_event(self, event: NotificationEvent) -> bool:
        """
        Process a notification event

        Args:
            event: Notification event

        Returns:
            True if event was processed successfully
        """
        try:
            logger.info(
                "processing_event",
                event_id=event.event_id,
                event_type=event.event_type,
                user_id=event.user_id,
            )

            # Get user preferences
            preferences = await self.preference_service.get_preferences(event.user_id)
            if not preferences:
                logger.warning("no_preferences_found", user_id=event.user_id)
                return False

            # Check if this type of notification is enabled
            notification_type = self._map_event_to_notification_type(event.event_type)
            if not await self.preference_service.is_notification_enabled(
                event.user_id, notification_type
            ):
                logger.info(
                    "notification_disabled",
                    user_id=event.user_id,
                    notification_type=notification_type,
                )
                return True  # Not an error, just skipped

            # Prepare notification data
            notification_data = self._prepare_notification_data(event, preferences)

            # Send notifications through enabled channels
            results = []

            if preferences.email_enabled and preferences.email_address:
                result = await self._send_email_notification(
                    event, notification_data, preferences.email_address
                )
                results.append(result)

            if preferences.telegram_enabled and preferences.telegram_chat_id:
                result = await self._send_telegram_notification(
                    event, notification_data, preferences.telegram_chat_id
                )
                results.append(result)

            if preferences.webhook_enabled and preferences.webhook_url:
                result = await self._send_webhook_notification(
                    event, notification_data, preferences.webhook_url, preferences.webhook_secret
                )
                results.append(result)

            # Consider event processed if at least one channel succeeded
            success = any(results) if results else False

            if success:
                logger.info(
                    "event_processed",
                    event_id=event.event_id,
                    channels_sent=sum(results),
                )
            else:
                logger.warning(
                    "event_processing_failed",
                    event_id=event.event_id,
                )

            return success

        except Exception as e:
            logger.error(
                "process_event_error",
                event_id=event.event_id,
                error=str(e),
            )
            return False

    def _map_event_to_notification_type(self, event_type: EventType) -> str:
        """Map event type to notification type"""
        mapping = {
            EventType.BUDGET_THRESHOLD_EXCEEDED: "budget_alert",
            EventType.BUDGET_THRESHOLD_WARNING: "budget_alert",
            EventType.TRANSACTION_CREATED: "transaction_created",
            EventType.TRANSACTION_LARGE: "transaction_created",
            EventType.PORTFOLIO_VALUE_CHANGED: "portfolio_alert",
            EventType.PRICE_TARGET_HIT: "price_alert",
            EventType.PRICE_ALERT: "price_alert",
            EventType.SYSTEM_UPDATE: "system_alert",
            EventType.SYSTEM_MAINTENANCE: "system_alert",
            EventType.USER_ACTION_REQUIRED: "system_alert",
        }
        return mapping.get(event_type, "custom")

    def _prepare_notification_data(
        self, event: NotificationEvent, preferences: Any
    ) -> Dict[str, Any]:
        """Prepare notification data from event"""
        data = event.data.copy()
        data["user_id"] = event.user_id
        data["event_type"] = event.event_type
        data["app_url"] = "http://localhost:3000"  # TODO: Make configurable
        return data

    async def _send_email_notification(
        self, event: NotificationEvent, data: Dict[str, Any], email: str
    ) -> bool:
        """Send email notification"""
        try:
            notification_type = self._map_event_to_notification_type(event.event_type)

            # Render email template
            plain_text, html = self.template_service.get_email_template(
                notification_type, data
            )

            # Send email
            return await self.email_service.send_email(
                to=email,
                subject=data.get("subject", f"FinCloud: {event.event_type}"),
                body=plain_text,
                html=html,
            )

        except Exception as e:
            logger.error("send_email_notification_failed", error=str(e))
            return False

    async def _send_telegram_notification(
        self, event: NotificationEvent, data: Dict[str, Any], chat_id: str
    ) -> bool:
        """Send Telegram notification"""
        try:
            # Format message for Telegram
            message = self._format_telegram_message(event, data)

            # Send message
            return await self.telegram_service.send_message(
                chat_id=chat_id,
                message=message,
                parse_mode="HTML",
            )

        except Exception as e:
            logger.error("send_telegram_notification_failed", error=str(e))
            return False

    def _format_telegram_message(
        self, event: NotificationEvent, data: Dict[str, Any]
    ) -> str:
        """Format message for Telegram"""
        subject = data.get("subject", event.event_type)
        message = data.get("message", "")

        return f"<b>{subject}</b>\n\n{message}"

    async def _send_webhook_notification(
        self, event: NotificationEvent, data: Dict[str, Any], url: str, secret: Optional[str]
    ) -> bool:
        """Send webhook notification"""
        try:
            payload = {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat(),
                "data": data,
            }

            return await self.webhook_service.send_webhook(
                url=url,
                payload=payload,
                secret=secret,
            )

        except Exception as e:
            logger.error("send_webhook_notification_failed", error=str(e))
            return False

    async def start_processing(self):
        """Start processing events from the queue"""
        self.processing = True
        logger.info("event_queue_processing_started")

        while self.processing:
            try:
                event = await self.dequeue_event()
                if event:
                    await self.process_event(event)
                else:
                    # No events in queue, wait before checking again
                    await asyncio.sleep(settings.EVENT_PROCESSING_INTERVAL)

            except Exception as e:
                logger.error("event_processing_loop_error", error=str(e))
                await asyncio.sleep(settings.EVENT_PROCESSING_INTERVAL)

    async def stop_processing(self):
        """Stop processing events"""
        self.processing = False
        logger.info("event_queue_processing_stopped")

    async def get_queue_length(self) -> int:
        """Get current queue length"""
        try:
            return await self.redis.llen(self.queue_name)
        except Exception:
            return 0
