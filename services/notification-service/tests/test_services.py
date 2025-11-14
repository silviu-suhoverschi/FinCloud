"""
Test notification services
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.email_service import EmailService
from app.services.telegram_service import TelegramService
from app.services.webhook_service import WebhookService
from app.services.template_service import TemplateService
from app.schemas.notification import EmailNotification, TelegramNotification, WebhookNotification


class TestEmailService:
    """Test email service"""

    def test_is_configured_false(self):
        """Test email service not configured"""
        with patch("app.services.email_service.settings") as mock_settings:
            mock_settings.SMTP_HOST = None
            mock_settings.SMTP_USER = None
            mock_settings.SMTP_PASSWORD = None

            service = EmailService()
            assert not service.is_configured()

    def test_is_configured_true(self):
        """Test email service configured"""
        with patch("app.services.email_service.settings") as mock_settings:
            mock_settings.SMTP_HOST = "smtp.example.com"
            mock_settings.SMTP_USER = "user@example.com"
            mock_settings.SMTP_PASSWORD = "password"
            mock_settings.SMTP_FROM_EMAIL = "from@example.com"
            mock_settings.SMTP_FROM_NAME = "Test"
            mock_settings.SMTP_USE_TLS = True

            service = EmailService()
            assert service.is_configured()

    @pytest.mark.asyncio
    async def test_send_email_not_configured(self):
        """Test sending email when not configured"""
        with patch("app.services.email_service.settings") as mock_settings:
            mock_settings.SMTP_HOST = None
            mock_settings.SMTP_USER = None
            mock_settings.SMTP_PASSWORD = None

            service = EmailService()
            result = await service.send_email(
                to="test@example.com",
                subject="Test",
                body="Test message",
            )

            assert not result


class TestTelegramService:
    """Test Telegram service"""

    def test_is_configured_false(self):
        """Test Telegram service not configured"""
        with patch("app.services.telegram_service.settings") as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = None

            service = TelegramService()
            assert not service.is_configured()

    def test_is_configured_true(self):
        """Test Telegram service configured"""
        with patch("app.services.telegram_service.settings") as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = "test-token"

            service = TelegramService()
            assert service.is_configured()

    @pytest.mark.asyncio
    async def test_send_message_not_configured(self):
        """Test sending message when not configured"""
        with patch("app.services.telegram_service.settings") as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = None

            service = TelegramService()
            result = await service.send_message(
                chat_id="123",
                message="Test message",
            )

            assert not result


class TestWebhookService:
    """Test webhook service"""

    @pytest.mark.asyncio
    async def test_send_webhook_success(self):
        """Test sending webhook successfully"""
        service = WebhookService()

        with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_client_instance = mock_client.return_value.__aenter__.return_value
            mock_client_instance.request = AsyncMock(return_value=mock_response)

            result = await service.send_webhook(
                url="https://example.com/webhook",
                payload={"test": "data"},
            )

            assert result

    @pytest.mark.asyncio
    async def test_send_webhook_with_signature(self):
        """Test sending webhook with signature"""
        service = WebhookService()

        with patch("app.services.webhook_service.httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_client_instance = mock_client.return_value.__aenter__.return_value
            mock_client_instance.request = AsyncMock(return_value=mock_response)

            result = await service.send_webhook(
                url="https://example.com/webhook",
                payload={"test": "data"},
                secret="my-secret-key",
            )

            assert result

    def test_generate_signature(self):
        """Test signature generation"""
        service = WebhookService()

        payload = '{"test": "data"}'
        secret = "my-secret"

        signature = service._generate_signature(payload, secret)

        assert signature
        assert len(signature) == 64  # SHA256 hex digest length


class TestTemplateService:
    """Test template service"""

    def test_currency_filter(self):
        """Test currency filter"""
        service = TemplateService()

        assert service._currency_filter(1000, "USD") == "$1,000.00"
        assert service._currency_filter(1500.50, "EUR") == "€1,500.50"
        assert service._currency_filter(2000, "GBP") == "£2,000.00"

    def test_render_string(self):
        """Test rendering template from string"""
        service = TemplateService()

        template = "Hello {{ name }}!"
        context = {"name": "World"}

        result = service.render_string(template, context)

        assert result == "Hello World!"

    def test_get_email_template(self):
        """Test getting email template"""
        service = TemplateService()

        context = {
            "subject": "Test Subject",
            "message": "Test Message",
        }

        plain_text, html = service.get_email_template("test_type", context)

        assert "Test Subject" in plain_text
        assert "Test Message" in plain_text
        assert "Test Subject" in html
        assert "Test Message" in html
