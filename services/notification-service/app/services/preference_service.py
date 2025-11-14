"""
Notification preferences service
"""
import json
from typing import Optional
import structlog
import redis.asyncio as redis

from app.schemas.preferences import NotificationPreferences, NotificationPreferencesUpdate

logger = structlog.get_logger()


class PreferenceService:
    """Notification preferences management service"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.key_prefix = "notification:preferences:"

    def _get_key(self, user_id: str) -> str:
        """Get Redis key for user preferences"""
        return f"{self.key_prefix}{user_id}"

    async def get_preferences(self, user_id: str) -> Optional[NotificationPreferences]:
        """
        Get user notification preferences

        Args:
            user_id: User ID

        Returns:
            NotificationPreferences or None if not found
        """
        try:
            key = self._get_key(user_id)
            data = await self.redis.get(key)

            if data:
                preferences_dict = json.loads(data)
                return NotificationPreferences(**preferences_dict)

            # Return default preferences if not found
            return NotificationPreferences(user_id=user_id)

        except Exception as e:
            logger.error(
                "get_preferences_failed",
                user_id=user_id,
                error=str(e),
            )
            return None

    async def update_preferences(
        self,
        user_id: str,
        preferences_update: NotificationPreferencesUpdate,
    ) -> Optional[NotificationPreferences]:
        """
        Update user notification preferences

        Args:
            user_id: User ID
            preferences_update: Preferences update data

        Returns:
            Updated NotificationPreferences or None on error
        """
        try:
            # Get current preferences
            current_prefs = await self.get_preferences(user_id)
            if not current_prefs:
                current_prefs = NotificationPreferences(user_id=user_id)

            # Update fields
            update_data = preferences_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(current_prefs, field, value)

            # Save to Redis
            key = self._get_key(user_id)
            await self.redis.set(
                key,
                current_prefs.model_dump_json(),
            )

            logger.info(
                "preferences_updated",
                user_id=user_id,
            )

            return current_prefs

        except Exception as e:
            logger.error(
                "update_preferences_failed",
                user_id=user_id,
                error=str(e),
            )
            return None

    async def delete_preferences(self, user_id: str) -> bool:
        """
        Delete user notification preferences

        Args:
            user_id: User ID

        Returns:
            True if deleted successfully
        """
        try:
            key = self._get_key(user_id)
            await self.redis.delete(key)

            logger.info(
                "preferences_deleted",
                user_id=user_id,
            )
            return True

        except Exception as e:
            logger.error(
                "delete_preferences_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def is_notification_enabled(
        self,
        user_id: str,
        notification_type: str,
    ) -> bool:
        """
        Check if notification type is enabled for user

        Args:
            user_id: User ID
            notification_type: Notification type

        Returns:
            True if enabled
        """
        preferences = await self.get_preferences(user_id)
        if not preferences:
            return True  # Default to enabled

        # Check type-specific settings
        type_mapping = {
            "budget_alert": preferences.budget_alerts_enabled,
            "transaction_created": preferences.transaction_alerts_enabled,
            "portfolio_alert": preferences.portfolio_alerts_enabled,
            "price_alert": preferences.price_alerts_enabled,
            "system_alert": preferences.system_alerts_enabled,
        }

        return type_mapping.get(notification_type, True)
