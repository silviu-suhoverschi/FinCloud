"""
Configuration settings for the Notification Service
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Service
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8003
    LOG_LEVEL: str = "info"
    ENVIRONMENT: str = "development"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/3"
    REDIS_MAX_CONNECTIONS: int = 10

    # Email/SMTP
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "FinCloud"
    SMTP_USE_TLS: bool = True

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None

    # WebPush (for future PWA notifications)
    VAPID_PUBLIC_KEY: Optional[str] = None
    VAPID_PRIVATE_KEY: Optional[str] = None
    VAPID_CLAIMS_EMAIL: Optional[str] = None

    # Webhook settings
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_MAX_RETRIES: int = 3
    WEBHOOK_RETRY_DELAY: int = 5

    # Event queue settings
    EVENT_QUEUE_NAME: str = "notifications:events"
    EVENT_PROCESSING_INTERVAL: int = 1  # seconds
    EVENT_BATCH_SIZE: int = 10

    # Notification settings
    MAX_NOTIFICATION_HISTORY: int = 1000
    NOTIFICATION_RETENTION_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
