"""
Pydantic schemas for the Notification Service
"""

from .event import (
    EventType,
    NotificationEvent,
)
from .notification import (
    EmailNotification,
    NotificationChannel,
    NotificationCreate,
    NotificationResponse,
    NotificationStatus,
    NotificationType,
    TelegramNotification,
    WebhookNotification,
)
from .preferences import (
    ChannelPreferences,
    NotificationPreferences,
    NotificationPreferencesUpdate,
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
