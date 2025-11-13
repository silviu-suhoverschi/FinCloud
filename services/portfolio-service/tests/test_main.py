"""
Tests for main application endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint"""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "FinCloud Portfolio Service"
    assert data["version"] == "0.1.0"
    assert "docs" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "portfolio-service"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_docs_available(client: AsyncClient):
    """Test that API documentation is available"""
    response = await client.get("/docs")
    assert response.status_code == 200

    response = await client.get("/redoc")
    assert response.status_code == 200
