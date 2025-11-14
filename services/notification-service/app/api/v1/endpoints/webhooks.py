"""
Webhook testing endpoints
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.notification import WebhookNotification
from app.services.webhook_service import WebhookService

logger = structlog.get_logger()

router = APIRouter()


def get_webhook_service():
    """Dependency to get webhook service"""
    return WebhookService()


@router.post("/test", status_code=status.HTTP_200_OK)
async def test_webhook(
    webhook: WebhookNotification,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    """
    Test a webhook URL
    """
    try:
        success = await webhook_service.send_notification(webhook)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send webhook",
            )

        return {
            "status": "success",
            "message": "Webhook sent successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("test_webhook_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test webhook: {str(e)}",
        ) from e
