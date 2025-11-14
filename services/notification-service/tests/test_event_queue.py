"""
Test event queue service
"""

from datetime import datetime

import pytest

from app.schemas.event import EventType, NotificationEvent
from app.services.event_queue import EventQueueService


@pytest.mark.asyncio
async def test_enqueue_event(
    redis_client,
    mock_email_service,
    mock_telegram_service,
    mock_webhook_service,
    sample_notification_event,
):
    """Test enqueueing an event"""
    from app.services.preference_service import PreferenceService
    from app.services.template_service import TemplateService

    template_service = TemplateService()
    preference_service = PreferenceService(redis_client)

    event_queue = EventQueueService(
        redis_client=redis_client,
        email_service=mock_email_service,
        telegram_service=mock_telegram_service,
        webhook_service=mock_webhook_service,
        template_service=template_service,
        preference_service=preference_service,
    )

    result = await event_queue.enqueue_event(sample_notification_event)

    assert result
    queue_length = await event_queue.get_queue_length()
    assert queue_length == 1


@pytest.mark.asyncio
async def test_dequeue_event(
    redis_client,
    mock_email_service,
    mock_telegram_service,
    mock_webhook_service,
    sample_notification_event,
):
    """Test dequeueing an event"""
    from app.services.preference_service import PreferenceService
    from app.services.template_service import TemplateService

    template_service = TemplateService()
    preference_service = PreferenceService(redis_client)

    event_queue = EventQueueService(
        redis_client=redis_client,
        email_service=mock_email_service,
        telegram_service=mock_telegram_service,
        webhook_service=mock_webhook_service,
        template_service=template_service,
        preference_service=preference_service,
    )

    # Enqueue first
    await event_queue.enqueue_event(sample_notification_event)

    # Dequeue
    event = await event_queue.dequeue_event()

    assert event is not None
    assert event.event_id == sample_notification_event.event_id
    assert event.event_type == sample_notification_event.event_type


@pytest.mark.asyncio
async def test_process_event(
    redis_client,
    mock_email_service,
    mock_telegram_service,
    mock_webhook_service,
    sample_notification_event,
    sample_notification_preferences,
):
    """Test processing an event"""
    from app.services.preference_service import PreferenceService
    from app.services.template_service import TemplateService

    template_service = TemplateService()
    preference_service = PreferenceService(redis_client)

    # Save preferences
    await preference_service.update_preferences(
        sample_notification_preferences.user_id,
        sample_notification_preferences,
    )

    event_queue = EventQueueService(
        redis_client=redis_client,
        email_service=mock_email_service,
        telegram_service=mock_telegram_service,
        webhook_service=mock_webhook_service,
        template_service=template_service,
        preference_service=preference_service,
    )

    result = await event_queue.process_event(sample_notification_event)

    assert result
    assert mock_email_service.send_email.called
    assert mock_telegram_service.send_message.called


@pytest.mark.asyncio
async def test_get_queue_length(
    redis_client,
    mock_email_service,
    mock_telegram_service,
    mock_webhook_service,
):
    """Test getting queue length"""
    from app.services.preference_service import PreferenceService
    from app.services.template_service import TemplateService

    template_service = TemplateService()
    preference_service = PreferenceService(redis_client)

    event_queue = EventQueueService(
        redis_client=redis_client,
        email_service=mock_email_service,
        telegram_service=mock_telegram_service,
        webhook_service=mock_webhook_service,
        template_service=template_service,
        preference_service=preference_service,
    )

    # Initially empty
    length = await event_queue.get_queue_length()
    assert length == 0

    # Add events
    event = NotificationEvent(
        event_id="test-1",
        event_type=EventType.SYSTEM_UPDATE,
        user_id="user-1",
        timestamp=datetime.utcnow(),
        data={"message": "Test"},
    )

    await event_queue.enqueue_event(event)
    length = await event_queue.get_queue_length()
    assert length == 1
