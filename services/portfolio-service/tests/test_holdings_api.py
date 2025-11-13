"""
Tests for Holdings API endpoints
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio
from app.models.asset import Asset
from app.models.holding import Holding
from app.core.auth import get_current_user_id
from app.main import app


# Mock user ID for testing (since we don't have User model in this service)
TEST_USER_ID = 1
TEST_USER_ID_2 = 2


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


@pytest_asyncio.fixture(scope="function")
async def test_asset(db_session: AsyncSession) -> Asset:
    """Create a test asset"""
    asset = Asset(
        symbol="AAPL",
        name="Apple Inc.",
        type="stock",
        asset_class="equity",
        sector="Technology",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        is_active=True,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset


@pytest_asyncio.fixture(scope="function")
async def test_asset_2(db_session: AsyncSession) -> Asset:
    """Create a second test asset"""
    asset = Asset(
        symbol="MSFT",
        name="Microsoft Corporation",
        type="stock",
        asset_class="equity",
        sector="Technology",
        exchange="NASDAQ",
        currency="USD",
        country="USA",
        is_active=True,
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset


@pytest_asyncio.fixture(scope="function")
async def test_holding(
    db_session: AsyncSession, test_portfolio: Portfolio, test_asset: Asset
) -> Holding:
    """Create a test holding"""
    holding = Holding(
        portfolio_id=test_portfolio.id,
        asset_id=test_asset.id,
        quantity=Decimal("10.0"),
        average_cost=Decimal("150.0"),
        cost_basis=Decimal("1500.0"),
        notes="Test holding",
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.mark.asyncio
async def test_list_holdings_empty(client: AsyncClient, mock_auth):
    """Test listing holdings when there are none"""
    response = await client.get("/api/v1/holdings/")
    assert response.status_code == 200
    data = response.json()
    assert "holdings" in data
    assert "total" in data
    assert isinstance(data["holdings"], list)
    assert data["total"] == 0
    assert len(data["holdings"]) == 0


@pytest.mark.asyncio
async def test_list_holdings_with_data(
    client: AsyncClient, mock_auth, test_holding: Holding
):
    """Test listing holdings with existing data"""
    response = await client.get("/api/v1/holdings/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["holdings"]) == 1
    assert data["holdings"][0]["quantity"] == "10.00000000"
    assert data["holdings"][0]["average_cost"] == "150.0000"


@pytest.mark.asyncio
async def test_list_holdings_pagination(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio, db_session
):
    """Test listing holdings with pagination"""
    # Create multiple assets and holdings
    for i in range(5):
        asset = Asset(
            symbol=f"STOCK{i}",
            name=f"Stock {i}",
            type="stock",
            currency="USD",
        )
        db_session.add(asset)
        await db_session.flush()

        holding = Holding(
            portfolio_id=test_portfolio.id,
            asset_id=asset.id,
            quantity=Decimal(f"{(i + 1) * 10}"),
            average_cost=Decimal("100.0"),
            cost_basis=Decimal(f"{(i + 1) * 1000}"),
        )
        db_session.add(holding)
    await db_session.commit()

    # Test with limit
    response = await client.get("/api/v1/holdings/?skip=0&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["holdings"]) == 3

    # Test with skip
    response = await client.get("/api/v1/holdings/?skip=3&limit=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["holdings"]) == 2


@pytest.mark.asyncio
async def test_list_holdings_filter_by_portfolio(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio, db_session
):
    """Test filtering holdings by portfolio ID"""
    # Create another portfolio
    portfolio2 = Portfolio(
        user_id=TEST_USER_ID, name="Portfolio 2", currency="USD"
    )
    db_session.add(portfolio2)
    await db_session.flush()

    # Create assets and holdings for both portfolios
    asset1 = Asset(symbol="AAPL", name="Apple", type="stock", currency="USD")
    asset2 = Asset(symbol="MSFT", name="Microsoft", type="stock", currency="USD")
    db_session.add(asset1)
    db_session.add(asset2)
    await db_session.flush()

    holding1 = Holding(
        portfolio_id=test_portfolio.id,
        asset_id=asset1.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150"),
        cost_basis=Decimal("1500"),
    )
    holding2 = Holding(
        portfolio_id=portfolio2.id,
        asset_id=asset2.id,
        quantity=Decimal("5"),
        average_cost=Decimal("200"),
        cost_basis=Decimal("1000"),
    )
    db_session.add(holding1)
    db_session.add(holding2)
    await db_session.commit()

    # Filter by first portfolio
    response = await client.get(f"/api/v1/holdings/?portfolio_id={test_portfolio.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["holdings"][0]["portfolio_id"] == test_portfolio.id

    # Filter by second portfolio
    response = await client.get(f"/api/v1/holdings/?portfolio_id={portfolio2.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["holdings"][0]["portfolio_id"] == portfolio2.id


@pytest.mark.asyncio
async def test_list_holdings_filter_by_asset(
    client: AsyncClient,
    mock_auth,
    test_portfolio: Portfolio,
    test_asset: Asset,
    test_asset_2: Asset,
    db_session,
):
    """Test filtering holdings by asset ID"""
    # Create holdings for both assets
    holding1 = Holding(
        portfolio_id=test_portfolio.id,
        asset_id=test_asset.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150"),
        cost_basis=Decimal("1500"),
    )
    holding2 = Holding(
        portfolio_id=test_portfolio.id,
        asset_id=test_asset_2.id,
        quantity=Decimal("5"),
        average_cost=Decimal("200"),
        cost_basis=Decimal("1000"),
    )
    db_session.add(holding1)
    db_session.add(holding2)
    await db_session.commit()

    # Filter by first asset
    response = await client.get(f"/api/v1/holdings/?asset_id={test_asset.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["holdings"][0]["asset_id"] == test_asset.id


@pytest.mark.asyncio
async def test_create_holding(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio, test_asset: Asset
):
    """Test creating a new holding"""
    holding_data = {
        "portfolio_id": test_portfolio.id,
        "asset_id": test_asset.id,
        "quantity": "15.5",
        "average_cost": "125.75",
        "notes": "New investment",
    }

    response = await client.post("/api/v1/holdings/", json=holding_data)
    assert response.status_code == 201
    data = response.json()
    assert data["portfolio_id"] == holding_data["portfolio_id"]
    assert data["asset_id"] == holding_data["asset_id"]
    assert data["quantity"] == "15.50000000"
    assert data["average_cost"] == "125.7500"
    assert data["cost_basis"] == "1949.12"  # 15.5 * 125.75
    assert data["notes"] == holding_data["notes"]
    assert "id" in data
    assert "uuid" in data


@pytest.mark.asyncio
async def test_create_holding_minimal(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio, test_asset: Asset
):
    """Test creating a holding with minimal data"""
    holding_data = {
        "portfolio_id": test_portfolio.id,
        "asset_id": test_asset.id,
        "quantity": "10.0",
    }

    response = await client.post("/api/v1/holdings/", json=holding_data)
    assert response.status_code == 201
    data = response.json()
    assert data["quantity"] == "10.00000000"
    assert data["average_cost"] == "0.0000"  # Default
    assert data["cost_basis"] == "0.00"
    assert data["notes"] is None


@pytest.mark.asyncio
async def test_create_holding_portfolio_not_found(
    client: AsyncClient, mock_auth, test_asset: Asset
):
    """Test creating a holding with non-existent portfolio"""
    holding_data = {
        "portfolio_id": 99999,
        "asset_id": test_asset.id,
        "quantity": "10.0",
    }

    response = await client.post("/api/v1/holdings/", json=holding_data)
    assert response.status_code == 404
    assert "portfolio" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_holding_asset_not_found(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio
):
    """Test creating a holding with non-existent asset"""
    holding_data = {
        "portfolio_id": test_portfolio.id,
        "asset_id": 99999,
        "quantity": "10.0",
    }

    response = await client.post("/api/v1/holdings/", json=holding_data)
    assert response.status_code == 404
    assert "asset" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_holding_duplicate(
    client: AsyncClient, mock_auth, test_holding: Holding
):
    """Test creating a duplicate holding fails"""
    holding_data = {
        "portfolio_id": test_holding.portfolio_id,
        "asset_id": test_holding.asset_id,
        "quantity": "5.0",
    }

    response = await client.post("/api/v1/holdings/", json=holding_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_holding_negative_quantity(
    client: AsyncClient, mock_auth, test_portfolio: Portfolio, test_asset: Asset
):
    """Test creating a holding with negative quantity fails"""
    holding_data = {
        "portfolio_id": test_portfolio.id,
        "asset_id": test_asset.id,
        "quantity": "-10.0",
    }

    response = await client.post("/api/v1/holdings/", json=holding_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_holding(client: AsyncClient, mock_auth, test_holding: Holding):
    """Test getting a holding by ID"""
    response = await client.get(f"/api/v1/holdings/{test_holding.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_holding.id
    assert data["portfolio_id"] == test_holding.portfolio_id
    assert data["asset_id"] == test_holding.asset_id
    assert data["quantity"] == "10.00000000"
    assert data["average_cost"] == "150.0000"


@pytest.mark.asyncio
async def test_get_holding_not_found(client: AsyncClient, mock_auth):
    """Test getting a non-existent holding"""
    response = await client.get("/api/v1/holdings/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_holding_unauthorized_user(
    client: AsyncClient, test_holding: Holding
):
    """Test getting a holding owned by another user"""

    async def override_get_current_user_id():
        return TEST_USER_ID_2

    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    response = await client.get(f"/api/v1/holdings/{test_holding.id}")
    assert response.status_code == 404  # Should not be visible to other users

    # Clean up
    del app.dependency_overrides[get_current_user_id]


@pytest.mark.asyncio
async def test_update_holding(client: AsyncClient, mock_auth, test_holding: Holding):
    """Test updating a holding"""
    update_data = {
        "quantity": "20.0",
        "average_cost": "160.0",
        "notes": "Updated holding",
    }

    response = await client.put(f"/api/v1/holdings/{test_holding.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == "20.00000000"
    assert data["average_cost"] == "160.0000"
    assert data["cost_basis"] == "3200.00"  # 20 * 160
    assert data["notes"] == update_data["notes"]


@pytest.mark.asyncio
async def test_update_holding_partial(
    client: AsyncClient, mock_auth, test_holding: Holding
):
    """Test partial update of a holding"""
    update_data = {
        "quantity": "15.0",
    }

    response = await client.put(f"/api/v1/holdings/{test_holding.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == "15.00000000"
    # Average cost should remain unchanged
    assert data["average_cost"] == "150.0000"
    # Cost basis should be recalculated
    assert data["cost_basis"] == "2250.00"  # 15 * 150


@pytest.mark.asyncio
async def test_update_holding_cost_basis_recalculation(
    client: AsyncClient, mock_auth, test_holding: Holding
):
    """Test that cost basis is recalculated on update"""
    # Update only average cost
    response = await client.put(
        f"/api/v1/holdings/{test_holding.id}", json={"average_cost": "200.0"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cost_basis"] == "2000.00"  # 10 * 200

    # Update only quantity
    response = await client.put(
        f"/api/v1/holdings/{test_holding.id}", json={"quantity": "25.0"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cost_basis"] == "5000.00"  # 25 * 200


@pytest.mark.asyncio
async def test_update_holding_not_found(client: AsyncClient, mock_auth):
    """Test updating a non-existent holding"""
    update_data = {"quantity": "10.0"}

    response = await client.put("/api/v1/holdings/99999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_holding_negative_values(
    client: AsyncClient, mock_auth, test_holding: Holding
):
    """Test updating holding with negative values fails"""
    update_data = {"quantity": "-5.0"}

    response = await client.put(f"/api/v1/holdings/{test_holding.id}", json=update_data)
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_delete_holding(client: AsyncClient, mock_auth, test_holding: Holding):
    """Test soft-deleting a holding"""
    response = await client.delete(f"/api/v1/holdings/{test_holding.id}")
    assert response.status_code == 204

    # Verify holding no longer appears in list
    response = await client.get("/api/v1/holdings/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0

    # Verify holding cannot be retrieved
    response = await client.get(f"/api/v1/holdings/{test_holding.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_holding_not_found(client: AsyncClient, mock_auth):
    """Test deleting a non-existent holding"""
    response = await client.delete("/api/v1/holdings/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_holdings_unauthorized(client: AsyncClient):
    """Test that endpoints require authentication"""
    response = await client.get("/api/v1/holdings/")
    assert response.status_code == 403  # No auth token provided
