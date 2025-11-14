"""
Webhook dispatcher service
"""

import hashlib
import hmac
from asyncio import sleep
from typing import Any

import httpx
import structlog

from app.core.config import settings
from app.schemas.notification import WebhookNotification

logger = structlog.get_logger()


class WebhookService:
    """Webhook notification service"""

    def __init__(self):
        self.timeout = settings.WEBHOOK_TIMEOUT
        self.max_retries = settings.WEBHOOK_MAX_RETRIES
        self.retry_delay = settings.WEBHOOK_RETRY_DELAY

    def _generate_signature(self, payload: str, secret: str) -> str:
        """
        Generate HMAC signature for webhook payload

        Args:
            payload: JSON payload as string
            secret: Secret key

        Returns:
            HMAC signature
        """
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    async def send_webhook(
        self,
        url: str,
        payload: dict[str, Any],
        method: str = "POST",
        headers: dict[str, str] | None = None,
        secret: str | None = None,
        retry_count: int = 0,
    ) -> bool:
        """
        Send webhook request

        Args:
            url: Webhook URL
            payload: JSON payload
            method: HTTP method
            headers: Additional headers
            secret: Secret for signature generation
            retry_count: Current retry attempt

        Returns:
            True if webhook was sent successfully
        """
        try:
            # Prepare headers
            request_headers = headers or {}
            request_headers["Content-Type"] = "application/json"
            request_headers["User-Agent"] = "FinCloud-Notification-Service/1.0"

            # Generate signature if secret is provided
            if secret:
                import json

                payload_str = json.dumps(payload, sort_keys=True)
                signature = self._generate_signature(payload_str, secret)
                request_headers["X-FinCloud-Signature"] = f"sha256={signature}"

            # Send request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    json=payload,
                    headers=request_headers,
                )

                # Check if request was successful
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(
                        "webhook_sent",
                        url=url,
                        status_code=response.status_code,
                        retry_count=retry_count,
                    )
                    return True
                else:
                    logger.warning(
                        "webhook_failed",
                        url=url,
                        status_code=response.status_code,
                        response=response.text[:200],
                    )
                    # Retry on server errors
                    if response.status_code >= 500 and retry_count < self.max_retries:
                        await sleep(self.retry_delay * (retry_count + 1))
                        return await self.send_webhook(
                            url=url,
                            payload=payload,
                            method=method,
                            headers=headers,
                            secret=secret,
                            retry_count=retry_count + 1,
                        )
                    return False

        except httpx.TimeoutException:
            logger.error("webhook_timeout", url=url, retry_count=retry_count)
            if retry_count < self.max_retries:
                await sleep(self.retry_delay * (retry_count + 1))
                return await self.send_webhook(
                    url=url,
                    payload=payload,
                    method=method,
                    headers=headers,
                    secret=secret,
                    retry_count=retry_count + 1,
                )
            return False

        except Exception as e:
            logger.error(
                "webhook_error",
                url=url,
                error=str(e),
                retry_count=retry_count,
            )
            return False

    async def send_notification(self, notification: WebhookNotification) -> bool:
        """
        Send webhook notification

        Args:
            notification: Webhook notification data

        Returns:
            True if webhook was sent successfully
        """
        return await self.send_webhook(
            url=notification.url,
            payload=notification.payload,
            method=notification.method,
            headers=notification.headers,
            secret=notification.secret,
        )
