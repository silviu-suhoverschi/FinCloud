"""
Test configuration and fixtures for API Gateway
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport, Response
import redis.asyncio as redis
from unittest.mock import AsyncMock, MagicMock, Mock

from app.main import app
from app.middleware.rate_limit import rate_limiter
from app.core.proxy import service_proxy


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the API Gateway"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def mock_redis():
    """Mock Redis client for rate limiting tests"""
    mock = AsyncMock(spec=redis.Redis)
    mock.ping = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    mock.pipeline = MagicMock()

    # Setup pipeline mock
    pipeline_mock = AsyncMock()
    pipeline_mock.incr = MagicMock(return_value=pipeline_mock)
    pipeline_mock.expire = MagicMock(return_value=pipeline_mock)
    pipeline_mock.execute = AsyncMock(return_value=[1, True])
    mock.pipeline.return_value = pipeline_mock

    # Temporarily replace the rate limiter's redis client
    original_client = rate_limiter.redis_client
    rate_limiter.redis_client = mock

    yield mock

    # Restore original client
    rate_limiter.redis_client = original_client


@pytest_asyncio.fixture
async def mock_service_proxy():
    """Mock service proxy for testing routing without actual backend services"""
    # Store original method
    original_proxy = service_proxy.proxy_request

    # Create a mock that raises service unavailable by default
    async def mock_proxy(*args, **kwargs):
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service unavailable (mocked)")

    service_proxy.proxy_request = mock_proxy

    yield service_proxy

    # Restore original method
    service_proxy.proxy_request = original_proxy


@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing"""
    from jose import jwt
    from app.core.config import settings

    payload = {
        "sub": "1",
        "email": "test@example.com",
        "role": "user",
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


@pytest.fixture
def expired_jwt_token():
    """Generate an expired JWT token for testing"""
    from jose import jwt
    from app.core.config import settings

    payload = {
        "sub": "1",
        "email": "test@example.com",
        "role": "user",
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=10)  # Expired
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


@pytest.fixture
def invalid_token_type():
    """Generate a token with wrong type (refresh instead of access)"""
    from jose import jwt
    from app.core.config import settings

    payload = {
        "sub": "1",
        "email": "test@example.com",
        "role": "user",
        "type": "refresh",  # Wrong type
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token
