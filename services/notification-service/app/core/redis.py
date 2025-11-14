"""
Redis connection management
"""

import redis.asyncio as redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()


class RedisManager:
    """Redis connection manager"""

    def __init__(self):
        self.redis_client: redis.Redis | None = None

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
            await self.redis_client.ping()
            logger.info("redis_connected", url=settings.REDIS_URL)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("redis_disconnected")

    def get_client(self) -> redis.Redis:
        """Get Redis client"""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
        return self.redis_client


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> redis.Redis:
    """Dependency to get Redis client"""
    return redis_manager.get_client()
