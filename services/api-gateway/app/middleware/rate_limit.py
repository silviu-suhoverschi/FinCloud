"""
Redis-based rate limiting middleware for API Gateway.
"""

import time
from typing import Optional
from fastapi import Request, HTTPException, status
import redis.asyncio as redis
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.RATE_LIMIT_ENABLED

    async def initialize(self):
        """Initialize Redis connection."""
        if not self.enabled:
            logger.info("Rate limiting disabled")
            return

        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Rate limiter initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize rate limiter", error=str(e))
            self.enabled = False

    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()

    async def check_rate_limit(self, request: Request) -> bool:
        """
        Check if request is within rate limits.

        Args:
            request: FastAPI request object

        Returns:
            bool: True if within limits, raises HTTPException otherwise
        """
        if not self.enabled or not self.redis_client:
            return True

        # Get client identifier (user_id or IP address)
        client_id = self._get_client_identifier(request)

        # Check both minute and hour limits
        current_time = int(time.time())

        # Check per-minute limit
        minute_key = f"rate_limit:minute:{client_id}:{current_time // 60}"
        minute_count = await self._increment_counter(minute_key, 60)

        if minute_count > settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(
                "Rate limit exceeded (per minute)",
                client_id=client_id,
                count=minute_count,
                limit=settings.RATE_LIMIT_PER_MINUTE,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {settings.RATE_LIMIT_PER_MINUTE} requests per minute",
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": str(
                        max(0, settings.RATE_LIMIT_PER_MINUTE - minute_count)
                    ),
                    "X-RateLimit-Reset": str((current_time // 60 + 1) * 60),
                    "Retry-After": str(60 - (current_time % 60)),
                },
            )

        # Check per-hour limit
        hour_key = f"rate_limit:hour:{client_id}:{current_time // 3600}"
        hour_count = await self._increment_counter(hour_key, 3600)

        if hour_count > settings.RATE_LIMIT_PER_HOUR:
            logger.warning(
                "Rate limit exceeded (per hour)",
                client_id=client_id,
                count=hour_count,
                limit=settings.RATE_LIMIT_PER_HOUR,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {settings.RATE_LIMIT_PER_HOUR} requests per hour",
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_HOUR),
                    "X-RateLimit-Remaining": str(
                        max(0, settings.RATE_LIMIT_PER_HOUR - hour_count)
                    ),
                    "X-RateLimit-Reset": str((current_time // 3600 + 1) * 3600),
                    "Retry-After": str(3600 - (current_time % 3600)),
                },
            )

        # Add rate limit headers to response
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit-Minute": str(settings.RATE_LIMIT_PER_MINUTE),
            "X-RateLimit-Remaining-Minute": str(
                max(0, settings.RATE_LIMIT_PER_MINUTE - minute_count)
            ),
            "X-RateLimit-Limit-Hour": str(settings.RATE_LIMIT_PER_HOUR),
            "X-RateLimit-Remaining-Hour": str(
                max(0, settings.RATE_LIMIT_PER_HOUR - hour_count)
            ),
        }

        return True

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client (user_id or IP).

        Args:
            request: FastAPI request object

        Returns:
            str: Client identifier
        """
        # Use user_id if authenticated
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"

        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        return f"ip:{client_ip}"

    async def _increment_counter(self, key: str, ttl: int) -> int:
        """
        Increment Redis counter with expiry.

        Args:
            key: Redis key
            ttl: Time to live in seconds

        Returns:
            int: Current counter value
        """
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, ttl)
            result = await pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(
                "Failed to increment rate limit counter", key=key, error=str(e)
            )
            # Fail open - allow request if Redis is down
            return 0


# Global rate limiter instance
rate_limiter = RateLimiter()
