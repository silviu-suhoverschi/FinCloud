"""
Telegram notification service
"""
from typing import Optional
import structlog
from telegram import Bot
from telegram.error import TelegramError

from app.core.config import settings
from app.schemas.notification import TelegramNotification

logger = structlog.get_logger()


class TelegramService:
    """Telegram notification service"""

    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.bot: Optional[Bot] = None
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)

    def is_configured(self) -> bool:
        """Check if Telegram service is properly configured"""
        return self.bot_token is not None and self.bot is not None

    async def send_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: str = "HTML",
        disable_notification: bool = False,
    ) -> bool:
        """
        Send a Telegram message

        Args:
            chat_id: Telegram chat ID
            message: Message text
            parse_mode: Parse mode (HTML, Markdown, MarkdownV2)
            disable_notification: Send message silently

        Returns:
            True if message was sent successfully
        """
        if not self.is_configured():
            logger.warning("telegram_service_not_configured")
            return False

        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
            )

            logger.info(
                "telegram_message_sent",
                chat_id=chat_id,
                message_length=len(message),
            )
            return True

        except TelegramError as e:
            logger.error(
                "telegram_send_failed",
                chat_id=chat_id,
                error=str(e),
            )
            return False
        except Exception as e:
            logger.error(
                "telegram_unexpected_error",
                chat_id=chat_id,
                error=str(e),
            )
            return False

    async def send_notification(self, notification: TelegramNotification) -> bool:
        """
        Send Telegram notification

        Args:
            notification: Telegram notification data

        Returns:
            True if message was sent successfully
        """
        return await self.send_message(
            chat_id=notification.chat_id,
            message=notification.message,
            parse_mode=notification.parse_mode,
            disable_notification=notification.disable_notification,
        )

    async def get_bot_info(self) -> Optional[dict]:
        """Get bot information"""
        if not self.is_configured():
            return None

        try:
            bot_info = await self.bot.get_me()
            return {
                "id": bot_info.id,
                "username": bot_info.username,
                "first_name": bot_info.first_name,
            }
        except Exception as e:
            logger.error("telegram_get_bot_info_failed", error=str(e))
            return None
