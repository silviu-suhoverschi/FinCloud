"""
Tests for rate limiting middleware
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_rate_limit_headers_present(client: AsyncClient, mock_redis):
    """Test that rate limit headers are added to responses"""
    response = await client.get("/")

    # Should have rate limit headers
    assert "x-ratelimit-limit-minute" in response.headers
    assert "x-ratelimit-remaining-minute" in response.headers
    assert "x-ratelimit-limit-hour" in response.headers
    assert "x-ratelimit-remaining-hour" in response.headers


@pytest.mark.asyncio
async def test_rate_limit_not_exceeded(client: AsyncClient, mock_redis):
    """Test request succeeds when under rate limit"""
    # Mock Redis to return low count
    pipeline_mock = AsyncMock()
    pipeline_mock.incr = lambda key: pipeline_mock
    pipeline_mock.expire = lambda key, ttl: pipeline_mock
    pipeline_mock.execute = AsyncMock(return_value=[5, True])  # Low count
    mock_redis.pipeline.return_value = pipeline_mock

    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_rate_limit_exceeded_per_minute(client: AsyncClient, mock_redis):
    """Test request is blocked when per-minute rate limit is exceeded"""
    from app.core.config import settings

    # Mock Redis to return count exceeding limit
    pipeline_mock = AsyncMock()
    pipeline_mock.incr = lambda key: pipeline_mock
    pipeline_mock.expire = lambda key, ttl: pipeline_mock
    pipeline_mock.execute = AsyncMock(
        return_value=[settings.RATE_LIMIT_PER_MINUTE + 1, True]
    )
    mock_redis.pipeline.return_value = pipeline_mock

    response = await client.get("/")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]
    assert "retry-after" in response.headers


@pytest.mark.asyncio
async def test_rate_limit_exceeded_per_hour(client: AsyncClient, mock_redis):
    """Test request is blocked when per-hour rate limit is exceeded"""
    from app.core.config import settings

    # Mock Redis to return count exceeding hourly limit but not minute
    pipeline_mock = AsyncMock()
    pipeline_mock.incr = lambda key: pipeline_mock
    pipeline_mock.expire = lambda key, ttl: pipeline_mock

    # First call (minute check) - pass
    # Second call (hour check) - exceed
    call_count = [0]

    async def execute_mock():
        call_count[0] += 1
        if call_count[0] == 1:
            return [10, True]  # Minute check - OK
        else:
            return [settings.RATE_LIMIT_PER_HOUR + 1, True]  # Hour check - exceeded

    pipeline_mock.execute = execute_mock
    mock_redis.pipeline.return_value = pipeline_mock

    response = await client.get("/")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]


@pytest.mark.asyncio
async def test_rate_limit_uses_user_id(
    client: AsyncClient, mock_redis, valid_jwt_token, mock_service_proxy
):
    """Test rate limiter uses user_id for authenticated requests"""
    from httpx import Response

    # Mock successful backend response
    mock_response = Response(
        status_code=200,
        json={"data": "test"},
        headers={"content-type": "application/json"},
    )
    mock_service_proxy.request = AsyncMock(return_value=mock_response)

    pipeline_mock = AsyncMock()
    pipeline_mock.incr = lambda key: pipeline_mock
    pipeline_mock.expire = lambda key, ttl: pipeline_mock
    pipeline_mock.execute = AsyncMock(return_value=[1, True])
    mock_redis.pipeline.return_value = pipeline_mock

    _ = await client.get(
        "/api/v1/budget/accounts",
        headers={"Authorization": f"Bearer {valid_jwt_token}"},
    )

    # Verify rate limiter was called
    assert mock_redis.pipeline.called


@pytest.mark.asyncio
async def test_rate_limit_uses_ip_for_unauthenticated(client: AsyncClient, mock_redis):
    """Test rate limiter uses IP address for unauthenticated requests"""
    pipeline_mock = AsyncMock()
    pipeline_mock.incr = lambda key: pipeline_mock
    pipeline_mock.expire = lambda key, ttl: pipeline_mock
    pipeline_mock.execute = AsyncMock(return_value=[1, True])
    mock_redis.pipeline.return_value = pipeline_mock

    _ = await client.get("/")

    # Verify rate limiter was called
    assert mock_redis.pipeline.called


@pytest.mark.asyncio
async def test_rate_limit_disabled(client: AsyncClient):
    """Test that requests work when rate limiting is disabled"""
    from app.middleware.rate_limit import rate_limiter

    # Disable rate limiting
    original_enabled = rate_limiter.enabled
    rate_limiter.enabled = False

    try:
        response = await client.get("/")
        assert response.status_code == 200
    finally:
        # Restore original state
        rate_limiter.enabled = original_enabled


@pytest.mark.asyncio
async def test_rate_limit_redis_failure_fails_open(client: AsyncClient, mock_redis):
    """Test that requests succeed if Redis fails (fail-open behavior)"""
    # Mock Redis to raise exception
    pipeline_mock = AsyncMock()
    pipeline_mock.incr = lambda key: pipeline_mock
    pipeline_mock.expire = lambda key, ttl: pipeline_mock
    pipeline_mock.execute = AsyncMock(side_effect=Exception("Redis error"))
    mock_redis.pipeline.return_value = pipeline_mock

    # Request should still succeed (fail-open)
    response = await client.get("/")
    assert response.status_code == 200
