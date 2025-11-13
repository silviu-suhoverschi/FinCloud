"""
Tests for Portfolio API endpoints
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.core.auth import get_current_user_id
from app.main import app


# Mock user ID for testing (since we don't have User model in this service)
TEST_USER_ID = 1


@pytest_asyncio.fixture(scope="function")
async def mock_auth():
    """Override authentication to return a test user ID"""

    async def override_get_current_user_id():
        return TEST_USER_ID

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    yield

    # Clean up
    if get_current_user_id in app.dependency_overrides:
        del app.dependency_overrides[get_current_user_id]


@pytest_asyncio.fixture(scope="function")
async def test_portfolio(db_session: AsyncSession) -> Portfolio:
    """Create a test portfolio"""
    portfolio = Portfolio(
        user_id=TEST_USER_ID,
        name="Test Portfolio",
        description="A test investment portfolio",
        currency="USD",
        is_active=True,
        sort_order=0,
    )
    db_session.add(portfolio)
    await db_session.commit()
    await db_session.refresh(portfolio)
    return portfolio


@pytest.mark.asyncio
async def test_list_portfolios_empty(client: AsyncClient, mock_auth):
    """Test listing portfolios when there are none"""
    response = await client.get("/api/v1/portfolios/")
    assert response.status_code == 200
    data = response.json()
    assert "portfolios" in data
    assert "total" in data
    assert isinstance(data["portfolios"], list)
    assert data["total"] == 0
    assert len(data["portfolios"]) == 0


@pytest.mark.asyncio
async def test_list_portfolios_with_data(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio
):
    """Test listing portfolios with existing data"""
    response = await client.get("/api/v1/portfolios/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["portfolios"]) == 1
    assert data["portfolios"][0]["name"] == "Test Portfolio"
    assert data["portfolios"][0]["currency"] == "USD"


@pytest.mark.asyncio
async def test_list_portfolios_pagination(client: AsyncClient, mock_auth, db_session):
    """Test listing portfolios with pagination"""
    # Create multiple portfolios
    for i in range(5):
        portfolio = Portfolio(
            user_id=TEST_USER_ID,
            name=f"Portfolio {i + 1}",
            currency="USD",
            sort_order=i,
        )
        db_session.add(portfolio)
    await db_session.commit()

    # Test with limit
    response = await client.get("/api/v1/portfolios/?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["portfolios"]) == 3

    # Test with skip
    response = await client.get("/api/v1/portfolios/?skip=3&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["portfolios"]) == 2


@pytest.mark.asyncio
async def test_list_portfolios_filter_active(
    client: AsyncClient, mock_auth, db_session
):
    """Test filtering portfolios by active status"""
    # Create active and inactive portfolios
    active = Portfolio(
        user_id=TEST_USER_ID, name="Active Portfolio", currency="USD", is_active=True
    )
    inactive = Portfolio(
        user_id=TEST_USER_ID,
        name="Inactive Portfolio",
        currency="USD",
        is_active=False,
    )
    db_session.add(active)
    db_session.add(inactive)
    await db_session.commit()

    # Filter for active only
    response = await client.get("/api/v1/portfolios/?is_active=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["portfolios"][0]["name"] == "Active Portfolio"

    # Filter for inactive only
    response = await client.get("/api/v1/portfolios/?is_active=false")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["portfolios"][0]["name"] == "Inactive Portfolio"


@pytest.mark.asyncio
async def test_create_portfolio(client: AsyncClient, mock_auth):
    """Test creating a new portfolio"""
    portfolio_data = {
        "name": "My Investment Portfolio",
        "description": "Long-term investment strategy",
        "currency": "USD",
        "is_active": True,
        "sort_order": 1,
    }

    response = await client.post("/api/v1/portfolios/", json=portfolio_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == portfolio_data["name"]
    assert data["description"] == portfolio_data["description"]
    assert data["currency"] == portfolio_data["currency"]
    assert data["is_active"] == portfolio_data["is_active"]
    assert data["sort_order"] == portfolio_data["sort_order"]
    assert "id" in data
    assert "uuid" in data
    assert data["user_id"] == TEST_USER_ID


@pytest.mark.asyncio
async def test_create_portfolio_minimal(client: AsyncClient, mock_auth):
    """Test creating a portfolio with minimal data"""
    portfolio_data = {
        "name": "Simple Portfolio",
    }

    response = await client.post("/api/v1/portfolios/", json=portfolio_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == portfolio_data["name"]
    assert data["currency"] == "USD"  # Default
    assert data["is_active"] is True  # Default
    assert data["sort_order"] == 0  # Default


@pytest.mark.asyncio
async def test_create_portfolio_duplicate_name(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio
):
    """Test creating a portfolio with duplicate name fails"""
    portfolio_data = {
        "name": test_portfolio.name,  # Same name as existing portfolio
        "currency": "USD",
    }

    response = await client.post("/api/v1/portfolios/", json=portfolio_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_portfolio_invalid_currency(client: AsyncClient, mock_auth):
    """Test creating a portfolio with invalid currency code"""
    portfolio_data = {
        "name": "Test Portfolio",
        "currency": "US",  # Invalid - must be 3 characters
    }

    response = await client.post("/api/v1/portfolios/", json=portfolio_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_portfolio(client: AsyncClient, mock_auth, test_portfolio: Portfolio):
    """Test getting a portfolio by ID"""
    response = await client.get(f"/api/v1/portfolios/{test_portfolio.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_portfolio.id
    assert data["name"] == test_portfolio.name
    assert data["description"] == test_portfolio.description
    assert data["currency"] == test_portfolio.currency


@pytest.mark.asyncio
async def test_get_portfolio_not_found(client: AsyncClient, mock_auth):
    """Test getting a non-existent portfolio"""
    response = await client.get("/api/v1/portfolios/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_portfolio(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio
):
    """Test updating a portfolio"""
    update_data = {
        "name": "Updated Portfolio Name",
        "description": "Updated description",
        "is_active": False,
    }

    response = await client.put(
        f"/api/v1/portfolios/{test_portfolio.id}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_active"] == update_data["is_active"]
    # Currency should remain unchanged
    assert data["currency"] == test_portfolio.currency


@pytest.mark.asyncio
async def test_update_portfolio_partial(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio
):
    """Test partial update of a portfolio"""
    update_data = {
        "name": "Partially Updated",
    }

    response = await client.put(
        f"/api/v1/portfolios/{test_portfolio.id}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    # Other fields should remain unchanged
    assert data["description"] == test_portfolio.description
    assert data["currency"] == test_portfolio.currency


@pytest.mark.asyncio
async def test_update_portfolio_duplicate_name(
    client: AsyncClient, mock_auth, db_session
):
    """Test updating portfolio to a name that already exists"""
    # Create two portfolios
    portfolio1 = Portfolio(
        user_id=TEST_USER_ID, name="Portfolio 1", currency="USD"
    )
    portfolio2 = Portfolio(
        user_id=TEST_USER_ID, name="Portfolio 2", currency="USD"
    )
    db_session.add(portfolio1)
    db_session.add(portfolio2)
    await db_session.commit()
    await db_session.refresh(portfolio1)
    await db_session.refresh(portfolio2)

    # Try to update portfolio2 to have the same name as portfolio1
    update_data = {"name": "Portfolio 1"}

    response = await client.put(f"/api/v1/portfolios/{portfolio2.id}", json=update_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_portfolio_not_found(client: AsyncClient, mock_auth):
    """Test updating a non-existent portfolio"""
    update_data = {"name": "Does Not Matter"}

    response = await client.put("/api/v1/portfolios/99999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_portfolio(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio
):
    """Test soft-deleting a portfolio"""
    response = await client.delete(f"/api/v1/portfolios/{test_portfolio.id}")
    assert response.status_code == 204

    # Verify portfolio no longer appears in list
    response = await client.get("/api/v1/portfolios/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0

    # Verify portfolio cannot be retrieved
    response = await client.get(f"/api/v1/portfolios/{test_portfolio.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_portfolio_not_found(client: AsyncClient, mock_auth):
    """Test deleting a non-existent portfolio"""
    response = await client.delete("/api/v1/portfolios/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_portfolios_unauthorized(client: AsyncClient):
    """Test that endpoints require authentication"""
    response = await client.get("/api/v1/portfolios/")
    assert response.status_code == 403  # No auth token provided
