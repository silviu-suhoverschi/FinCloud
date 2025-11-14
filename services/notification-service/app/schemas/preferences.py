"""
Notification preferences schemas
"""

from pydantic import BaseModel, EmailStr


class ChannelPreferences(BaseModel):
    """Channel-specific preferences"""

    enabled: bool = True
    email: EmailStr | None = None
    telegram_chat_id: str | None = None
    webhook_url: str | None = None


class NotificationPreferences(BaseModel):
    """User notification preferences"""

    user_id: str
    email_enabled: bool = True
    telegram_enabled: bool = False
    webhook_enabled: bool = False
    webpush_enabled: bool = False

    # Email settings
    email_address: EmailStr | None = None

    # Telegram settings
    telegram_chat_id: str | None = None

    # Webhook settings
    webhook_url: str | None = None
    webhook_secret: str | None = None

    # Type-specific preferences
    budget_alerts_enabled: bool = True
    transaction_alerts_enabled: bool = True
    portfolio_alerts_enabled: bool = True
    price_alerts_enabled: bool = True
    system_alerts_enabled: bool = True

    # Quiet hours
    quiet_hours_enabled: bool = False
    quiet_hours_start: str | None = None  # HH:MM format
    quiet_hours_end: str | None = None  # HH:MM format

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
                "quiet_hours_end": "08:00",
            }
        }


class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences"""

    email_enabled: bool | None = None
    telegram_enabled: bool | None = None
    webhook_enabled: bool | None = None
    webpush_enabled: bool | None = None

    email_address: EmailStr | None = None
    telegram_chat_id: str | None = None
    webhook_url: str | None = None
    webhook_secret: str | None = None

    budget_alerts_enabled: bool | None = None
    transaction_alerts_enabled: bool | None = None
    portfolio_alerts_enabled: bool | None = None
    price_alerts_enabled: bool | None = None
    system_alerts_enabled: bool | None = None

    quiet_hours_enabled: bool | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
