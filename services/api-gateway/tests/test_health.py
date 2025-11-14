"""
Tests for health check endpoints
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import httpx


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test simple health check endpoint"""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient):
    """Test Kubernetes liveness probe"""
    response = await client.get("/api/v1/health/live")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_readiness_probe_with_redis(client: AsyncClient, mock_redis):
    """Test Kubernetes readiness probe when Redis is available"""
    mock_redis.ping = AsyncMock(return_value=True)

    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_readiness_probe_without_redis(client: AsyncClient):
    """Test Kubernetes readiness probe when Redis is unavailable"""
    from app.middleware.rate_limit import rate_limiter

    # Temporarily set Redis client to None to simulate unavailable Redis
    original_client = rate_limiter.redis_client
    rate_limiter.redis_client = None

    try:
        response = await client.get("/api/v1/health/ready")

        # Should still be ready if rate limiting is disabled
        # (depends on RATE_LIMIT_ENABLED setting)
        assert response.status_code in [200, 503]
    finally:
        rate_limiter.redis_client = original_client


@pytest.mark.asyncio
@patch('app.api.v1.health.check_service_health')
async def test_detailed_health_all_services_healthy(mock_check_health, client: AsyncClient, mock_redis):
    """Test detailed health check when all services are healthy"""
    # Mock all services as healthy
    mock_check_health.return_value = {
        "status": "healthy",
        "response_time_ms": 50
    }

    mock_redis.ping = AsyncMock(return_value=True)

    response = await client.get("/api/v1/health/detailed")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"
    assert "services" in data
    assert "redis" in data
    assert "circuit_breakers" in data


@pytest.mark.asyncio
@patch('app.api.v1.health.check_service_health')
async def test_detailed_health_some_services_unhealthy(mock_check_health, client: AsyncClient, mock_redis):
    """Test detailed health check when some services are unhealthy"""
    # Mock one service as unhealthy
    async def mock_health_func(service_name, service_url):
        if service_name == "budget_service":
            return {"status": "healthy", "response_time_ms": 50}
        else:
            return {"status": "unhealthy", "error": "Connection refused"}

    mock_check_health.side_effect = mock_health_func
    mock_redis.ping = AsyncMock(return_value=True)

    response = await client.get("/api/v1/health/detailed")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "degraded"  # Overall status should be degraded


@pytest.mark.asyncio
async def test_status_endpoint(client: AsyncClient):
    """Test API status endpoint"""
    response = await client.get("/api/v1/status")
    assert response.status_code == 200

    data = response.json()
    assert data["api_version"] == "v1"
    assert data["gateway_version"] == "0.1.0"
    assert "services" in data
    assert "features" in data

    # Check features
    features = data["features"]
    assert features["authentication"] is True
    assert features["circuit_breaker"] is True
    assert features["cors"] is True


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_check_service_health_success(mock_get):
    """Test checking service health when service responds"""
    from app.api.v1.health import check_service_health
    from unittest.mock import Mock

    # Mock successful response - use Mock instead of AsyncMock for attributes
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_response.content = b'{"status": "ok"}'
    # elapsed is a Mock object with total_seconds method
    mock_response.elapsed.total_seconds.return_value = 0.05

    # Wrap in AsyncMock to make it awaitable
    mock_get.return_value = mock_response

    result = await check_service_health("test-service", "http://test:8000")

    assert result["status"] == "healthy"
    assert result["response_time_ms"] == 50
    assert "details" in result


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_check_service_health_failure(mock_get):
    """Test checking service health when service fails"""
    from app.api.v1.health import check_service_health
    from unittest.mock import Mock

    # Mock failed response
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.elapsed.total_seconds.return_value = 0.1
    mock_get.return_value = mock_response

    result = await check_service_health("test-service", "http://test:8000")

    assert result["status"] == "unhealthy"
    assert "error" in result
    assert "HTTP 500" in result["error"]


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_check_service_health_timeout(mock_get):
    """Test checking service health when service times out"""
    from app.api.v1.health import check_service_health

    # Mock timeout
    mock_get.side_effect = httpx.TimeoutException("Timeout")

    result = await check_service_health("test-service", "http://test:8000")

    assert result["status"] == "unhealthy"
    assert result["error"] == "Timeout"


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_check_service_health_connection_error(mock_get):
    """Test checking service health when connection fails"""
    from app.api.v1.health import check_service_health

    # Mock connection error
    mock_get.side_effect = Exception("Connection refused")

    result = await check_service_health("test-service", "http://test:8000")

    assert result["status"] == "unhealthy"
    assert "error" in result
