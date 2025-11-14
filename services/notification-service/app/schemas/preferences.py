"""
Notification preferences schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from app.schemas.notification import NotificationChannel, NotificationType


class ChannelPreferences(BaseModel):
    """Channel-specific preferences"""
    enabled: bool = True
    email: Optional[EmailStr] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None


class NotificationPreferences(BaseModel):
    """User notification preferences"""
    user_id: str
    email_enabled: bool = True
    telegram_enabled: bool = False
    webhook_enabled: bool = False
    webpush_enabled: bool = False

    # Email settings
    email_address: Optional[EmailStr] = None

    # Telegram settings
    telegram_chat_id: Optional[str] = None

    # Webhook settings
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

    # Type-specific preferences
    budget_alerts_enabled: bool = True
    transaction_alerts_enabled: bool = True
    portfolio_alerts_enabled: bool = True
    price_alerts_enabled: bool = True
    system_alerts_enabled: bool = True

    # Quiet hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM format
    quiet_hours_end: Optional[str] = None  # HH:MM format

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "email_enabled": True,
                "telegram_enabled": True,
                "email_address": "user@example.com",
                "telegram_chat_id": "123456789",
                "budget_alerts_enabled": True,
                "transaction_alerts_enabled": False,
                "quiet_hours_enabled": True,
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "08:00"
            }
        }


class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences"""
    email_enabled: Optional[bool] = None
    telegram_enabled: Optional[bool] = None
    webhook_enabled: Optional[bool] = None
    webpush_enabled: Optional[bool] = None

    email_address: Optional[EmailStr] = None
    telegram_chat_id: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

    budget_alerts_enabled: Optional[bool] = None
    transaction_alerts_enabled: Optional[bool] = None
    portfolio_alerts_enabled: Optional[bool] = None
    price_alerts_enabled: Optional[bool] = None
    system_alerts_enabled: Optional[bool] = None

    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
