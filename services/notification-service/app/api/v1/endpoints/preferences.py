"""
Notification preferences endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path
import structlog

from app.schemas.preferences import (
    NotificationPreferences,
    NotificationPreferencesUpdate,
)
from app.core.redis import get_redis
from app.services.preference_service import PreferenceService
import redis.asyncio as redis

logger = structlog.get_logger()

router = APIRouter()


async def get_preference_service(redis_client: redis.Redis = Depends(get_redis)):
    """Dependency to get preference service"""
    return PreferenceService(redis_client)


@router.get("/{user_id}", response_model=NotificationPreferences)
async def get_preferences(
    user_id: str = Path(..., description="User ID"),
    preference_service: PreferenceService = Depends(get_preference_service),
):
    """
    Get notification preferences for a user
    """
    try:
        preferences = await preference_service.get_preferences(user_id)

        if not preferences:
            # Return default preferences
            preferences = NotificationPreferences(user_id=user_id)

        return preferences

    except Exception as e:
        logger.error("get_preferences_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}",
        )


@router.put("/{user_id}", response_model=NotificationPreferences)
async def update_preferences(
    user_id: str = Path(..., description="User ID"),
    preferences_update: NotificationPreferencesUpdate = ...,
    preference_service: PreferenceService = Depends(get_preference_service),
):
    """
    Update notification preferences for a user
    """
    try:
        preferences = await preference_service.update_preferences(
            user_id, preferences_update
        )

        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update preferences",
            )

        return preferences

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_preferences_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preferences(
    user_id: str = Path(..., description="User ID"),
    preference_service: PreferenceService = Depends(get_preference_service),
):
    """
    Delete notification preferences for a user (resets to defaults)
    """
    try:
        success = await preference_service.delete_preferences(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete preferences",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_preferences_failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete preferences: {str(e)}",
        )
