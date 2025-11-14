"""
Configuration management for API Gateway
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    SERVICE_NAME: str = "api-gateway"
    SERVICE_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Redis
    REDIS_URL: str = "redis://localhost:6379/4"  # DB 4 for API Gateway

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Service URLs
    BUDGET_SERVICE_URL: str = "http://budget-service:8001"
    PORTFOLIO_SERVICE_URL: str = "http://portfolio-service:8002"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8003"

    # Circuit Breaker Settings
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60  # seconds
    CIRCUIT_BREAKER_EXPECTED_EXCEPTION: int = 500

    # Request Timeout
    REQUEST_TIMEOUT: int = 30  # seconds

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
