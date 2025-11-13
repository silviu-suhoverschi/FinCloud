"""
Tests for API endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_portfolios(client: AsyncClient):
    """Test listing portfolios endpoint"""
    response = await client.get("/api/v1/portfolios/")
    assert response.status_code == 200
    data = response.json()
    assert "portfolios" in data
    assert isinstance(data["portfolios"], list)


@pytest.mark.asyncio
async def test_create_portfolio(client: AsyncClient):
    """Test creating a portfolio endpoint"""
    response = await client.post("/api/v1/portfolios/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_get_portfolio(client: AsyncClient):
    """Test getting a portfolio by ID endpoint"""
    portfolio_id = 1
    response = await client.get(f"/api/v1/portfolios/{portfolio_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["portfolio_id"] == portfolio_id
