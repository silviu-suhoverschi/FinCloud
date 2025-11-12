"""
Configuration management for Portfolio Service
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    SERVICE_NAME: str = "portfolio-service"
    SERVICE_PORT: int = 8002
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://fincloud:fincloud_dev_password@localhost:5432/fincloud"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/1"
    CELERY_BROKER_URL: str = "redis://localhost:6379/2"

    # API Keys
    ALPHA_VANTAGE_API_KEY: str = "demo"
    COINGECKO_API_KEY: str = ""
    YAHOO_FINANCE_ENABLED: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
