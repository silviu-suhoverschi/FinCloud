"""
Test configuration and fixtures
"""

from unittest.mock import AsyncMock, MagicMock

import fakeredis.aioredis
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def test_client():
    """Get test client"""
    return TestClient(app)


@pytest_asyncio.fixture
async def redis_client():
    """Get fake Redis client for testing"""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    # Ensure clean state for each test
    await client.flushdb()
    yield client
    await client.aclose()


@pytest.fixture
def mock_email_service():
    """Mock email service"""
    from app.services.email_service import EmailService

    service = EmailService()
    service.send_email = AsyncMock(return_value=True)
    service.send_notification = AsyncMock(return_value=True)
    service.is_configured = MagicMock(return_value=True)
    return service


@pytest.fixture
def mock_telegram_service():
    """Mock Telegram service"""
    from app.services.telegram_service import TelegramService

    service = TelegramService()
    service.send_message = AsyncMock(return_value=True)
    service.send_notification = AsyncMock(return_value=True)
    service.is_configured = MagicMock(return_value=True)
    return service


@pytest.fixture
def mock_webhook_service():
    """Mock webhook service"""
    from app.services.webhook_service import WebhookService

    service = WebhookService()
    service.send_webhook = AsyncMock(return_value=True)
    service.send_notification = AsyncMock(return_value=True)
    return service


@pytest.fixture
def sample_notification_event():
    """Sample notification event"""
    from datetime import datetime

    from app.schemas.event import EventType, NotificationEvent

    return NotificationEvent(
        event_id="test-event-123",
        event_type=EventType.BUDGET_THRESHOLD_EXCEEDED,
        user_id="test-user-123",
        timestamp=datetime.utcnow(),
        data={
            "budget_name": "Groceries",
            "spent": 520.00,
            "limit": 500.00,
            "percentage": 104.0,
            "remaining": -20.00,
            "currency": "USD",
            "budget_id": "budget-123",
            "subject": "Budget Alert: Groceries",
            "message": "You have exceeded your budget limit.",
        },
        priority=2,
    )


@pytest.fixture
def sample_notification_preferences():
    """Sample notification preferences"""
    from app.schemas.preferences import NotificationPreferences

    return NotificationPreferences(
        user_id="test-user-123",
        email_enabled=True,
        telegram_enabled=True,
        webhook_enabled=False,
        email_address="test@example.com",
        telegram_chat_id="123456789",
        budget_alerts_enabled=True,
        transaction_alerts_enabled=True,
        portfolio_alerts_enabled=True,
    )
