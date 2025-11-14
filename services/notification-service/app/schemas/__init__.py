"""
Pydantic schemas for the Notification Service
"""
from .notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationType,
    NotificationStatus,
    NotificationChannel,
    EmailNotification,
    TelegramNotification,
    WebhookNotification,
)
from .preferences import (
    NotificationPreferences,
    NotificationPreferencesUpdate,
    ChannelPreferences,
)
from .event import (
    NotificationEvent,
    EventType,
)

__all__ = [
    "NotificationCreate",
    "NotificationResponse",
    "NotificationType",
    "NotificationStatus",
    "NotificationChannel",
    "EmailNotification",
    "TelegramNotification",
    "WebhookNotification",
    "NotificationPreferences",
    "NotificationPreferencesUpdate",
    "ChannelPreferences",
    "NotificationEvent",
    "EventType",
]
