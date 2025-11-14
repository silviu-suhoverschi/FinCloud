"""
Test API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


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


@pytest.mark.asyncio
async def test_send_notification(client):
    """Test send notification endpoint"""
    with patch("app.api.v1.endpoints.notifications.get_event_queue_service") as mock_service:
        mock_queue = AsyncMock()
        mock_queue.enqueue_event = AsyncMock(return_value=True)
        mock_service.return_value = mock_queue

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


@pytest.mark.asyncio
async def test_get_preferences(client):
    """Test get preferences endpoint"""
    with patch("app.api.v1.endpoints.preferences.get_preference_service") as mock_service:
        from app.schemas.preferences import NotificationPreferences

        mock_pref_service = AsyncMock()
        mock_pref_service.get_preferences = AsyncMock(
            return_value=NotificationPreferences(user_id="test-user")
        )
        mock_service.return_value = mock_pref_service

        response = client.get("/api/v1/preferences/test-user")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"


@pytest.mark.asyncio
async def test_update_preferences(client):
    """Test update preferences endpoint"""
    with patch("app.api.v1.endpoints.preferences.get_preference_service") as mock_service:
        from app.schemas.preferences import NotificationPreferences

        mock_pref_service = AsyncMock()
        updated_prefs = NotificationPreferences(
            user_id="test-user", email_enabled=False
        )
        mock_pref_service.update_preferences = AsyncMock(return_value=updated_prefs)
        mock_service.return_value = mock_pref_service

        update_data = {"email_enabled": False}

        response = client.put("/api/v1/preferences/test-user", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user"
