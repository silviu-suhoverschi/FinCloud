"""
Test preference service
"""
import pytest

from app.services.preference_service import PreferenceService
from app.schemas.preferences import NotificationPreferences, NotificationPreferencesUpdate


@pytest.mark.asyncio
async def test_get_preferences_default(redis_client):
    """Test getting default preferences"""
    service = PreferenceService(redis_client)

    preferences = await service.get_preferences("test-user")

    assert preferences is not None
    assert preferences.user_id == "test-user"
    assert preferences.email_enabled
    assert not preferences.telegram_enabled


@pytest.mark.asyncio
async def test_update_preferences(redis_client):
    """Test updating preferences"""
    service = PreferenceService(redis_client)

    update = NotificationPreferencesUpdate(
        email_enabled=False,
        telegram_enabled=True,
        telegram_chat_id="123456789",
    )

    preferences = await service.update_preferences("test-user", update)

    assert preferences is not None
    assert not preferences.email_enabled
    assert preferences.telegram_enabled
    assert preferences.telegram_chat_id == "123456789"


@pytest.mark.asyncio
async def test_delete_preferences(redis_client):
    """Test deleting preferences"""
    service = PreferenceService(redis_client)

    # Create preferences
    update = NotificationPreferencesUpdate(email_enabled=False)
    await service.update_preferences("test-user", update)

    # Delete
    result = await service.delete_preferences("test-user")

    assert result

    # Should return default after deletion
    preferences = await service.get_preferences("test-user")
    assert preferences.email_enabled  # Back to default


@pytest.mark.asyncio
async def test_is_notification_enabled(redis_client):
    """Test checking if notification type is enabled"""
    service = PreferenceService(redis_client)

    # Update preferences to disable budget alerts
    update = NotificationPreferencesUpdate(budget_alerts_enabled=False)
    await service.update_preferences("test-user", update)

    # Check
    enabled = await service.is_notification_enabled("test-user", "budget_alert")
    assert not enabled

    # Check other types (should be enabled by default)
    enabled = await service.is_notification_enabled("test-user", "transaction_created")
    assert enabled
