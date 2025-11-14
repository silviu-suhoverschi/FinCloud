"""
Test API endpoints
"""

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from app.core.redis import get_redis
from app.main import app


@pytest.fixture
def mock_redis():
    """Mock Redis client for API tests"""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture
def client(mock_redis):
    """Test client with mocked Redis"""
    app.dependency_overrides[get_redis] = lambda: mock_redis
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "notification-service"
    assert data["status"] == "operational"


def test_health_check(client):
    """Test health check endpoint"""
    # Health check might fail without Redis, so we just check it responds
    response = client.get("/health")
    assert response.status_code == 200


def test_service_info(client):
    """Test service info endpoint"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "notification-service"
    assert "features" in data


def test_send_notification(client):
    """Test send notification endpoint"""
    notification_data = {
        "user_id": "test-user-123",
        "notification_type": "budget_alert",
        "channels": ["email"],
        "subject": "Budget Alert",
        "message": "Test message",
        "priority": 1,
    }

    response = client.post("/api/v1/notifications/send", json=notification_data)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert "event_id" in data


def test_get_preferences(client):
    """Test get preferences endpoint"""
    response = client.get("/api/v1/preferences/test-user")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user"
    # Default preferences
    assert data["email_enabled"] is True


def test_update_preferences(client):
    """Test update preferences endpoint"""
    update_data = {"email_enabled": False, "telegram_enabled": True}

    response = client.put("/api/v1/preferences/test-user", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "test-user"
    assert data["email_enabled"] is False
    assert data["telegram_enabled"] is True
