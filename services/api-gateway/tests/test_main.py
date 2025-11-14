"""
Tests for main API Gateway application
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint returns service information"""
    response = await client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "api-gateway"
    assert data["version"] == "0.1.0"
    assert data["status"] == "operational"
    assert "documentation" in data
    assert "services" in data


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-gateway"


@pytest.mark.asyncio
async def test_api_status_endpoint(client: AsyncClient):
    """Test API status endpoint"""
    response = await client.get("/api/v1/status")
    assert response.status_code == 200

    data = response.json()
    assert data["api_version"] == "v1"
    assert "services" in data
    assert "features" in data
    assert data["features"]["authentication"] is True
    assert data["features"]["circuit_breaker"] is True


@pytest.mark.asyncio
async def test_openapi_docs(client: AsyncClient):
    """Test OpenAPI documentation is available"""
    response = await client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert data["info"]["title"] == "FinCloud API Gateway"
    assert data["info"]["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_cors_headers(client: AsyncClient):
    """Test CORS headers are present"""
    response = await client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_request_id_header(client: AsyncClient):
    """Test that request ID is added to response headers"""
    response = await client.get("/")
    assert "x-request-id" in response.headers
    assert "x-process-time" in response.headers
