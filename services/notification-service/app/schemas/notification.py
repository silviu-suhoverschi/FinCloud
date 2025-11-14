"""
Notification schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


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
    channels: List[NotificationChannel] = Field(default_factory=list)
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1)
    data: Optional[Dict[str, Any]] = None
    priority: int = Field(default=1, ge=1, le=5)


class NotificationResponse(BaseModel):
    """Notification response"""
    id: str
    user_id: str
    notification_type: NotificationType
    channels: List[NotificationChannel]
    subject: str
    message: str
    data: Optional[Dict[str, Any]] = None
    status: NotificationStatus
    priority: int
    created_at: datetime
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None


class EmailNotification(BaseModel):
    """Email notification data"""
    to: EmailStr
    subject: str
    body: str
    html: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[str]] = None


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
    headers: Optional[Dict[str, str]] = None
    payload: Dict[str, Any]
    secret: Optional[str] = None


class SendNotificationRequest(BaseModel):
    """Send notification request"""
    notification: NotificationCreate
