"""
Notification schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class NotificationType(str, Enum):
    """Notification types"""

    BUDGET_ALERT = "budget_alert"
    TRANSACTION_CREATED = "transaction_created"
    PORTFOLIO_ALERT = "portfolio_alert"
    PRICE_ALERT = "price_alert"
    SYSTEM_ALERT = "system_alert"
    CUSTOM = "custom"


class NotificationChannel(str, Enum):
    """Notification channels"""

    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    WEBPUSH = "webpush"


class NotificationStatus(str, Enum):
    """Notification status"""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"


class NotificationCreate(BaseModel):
    """Create notification request"""

    user_id: str
    notification_type: NotificationType
    channels: list[NotificationChannel] = Field(default_factory=list)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    data: dict[str, Any] | None = None
    priority: int = Field(default=1, ge=1, le=5)


class NotificationResponse(BaseModel):
    """Notification response"""

    id: str
    user_id: str
    notification_type: NotificationType
    channels: list[NotificationChannel]
    subject: str
    message: str
    data: dict[str, Any] | None = None
    status: NotificationStatus
    priority: int
    created_at: datetime
    sent_at: datetime | None = None
    error_message: str | None = None


class EmailNotification(BaseModel):
    """Email notification data"""

    to: EmailStr
    subject: str
    body: str
    html: str | None = None
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    attachments: list[str] | None = None


class TelegramNotification(BaseModel):
    """Telegram notification data"""

    chat_id: str
    message: str
    parse_mode: str = "HTML"
    disable_notification: bool = False


class WebhookNotification(BaseModel):
    """Webhook notification data"""

    url: str
    method: str = "POST"
    headers: dict[str, str] | None = None
    payload: dict[str, Any]
    secret: str | None = None


class SendNotificationRequest(BaseModel):
    """Send notification request"""

    notification: NotificationCreate
