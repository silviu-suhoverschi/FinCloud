"""
Tests for portfolio analytics service
"""

import pytest
import pytest_asyncio
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import AnalyticsService
from app.models.portfolio import Portfolio
from app.models.asset import Asset
from app.models.holding import Holding
from app.models.portfolio_transaction import PortfolioTransaction
from app.core.auth import get_current_user
from app.main import app


# Mock user for testing
TEST_USER_ID = 1


@pytest_asyncio.fixture(scope="function")
async def mock_auth():
    """Override authentication to return a test user"""

    async def override_get_current_user():
        return {
            "id": TEST_USER_ID,
            "email": "test@example.com",
            "role": "user",
        }

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield

    # Clean up
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.mark.asyncio
async def test_get_portfolio_total_value_empty(db_session: AsyncSession):
    """Test portfolio total value calculation for empty portfolio"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.commit()
    await db_session.refresh(portfolio)

    analytics_service = AnalyticsService(db_session)
    total_value = await analytics_service.get_portfolio_total_value(portfolio.id)

    assert total_value == Decimal("0")


@pytest.mark.asyncio
async def test_get_portfolio_total_value_with_holdings(db_session: AsyncSession):
    """Test portfolio total value calculation with holdings"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create assets
    asset1 = Asset(
        symbol="AAPL",
        name="Apple Inc.",
        type="stock",
        currency="USD"
    )
    asset2 = Asset(
        symbol="GOOGL",
        name="Alphabet Inc.",
        type="stock",
        currency="USD"
    )
    db_session.add_all([asset1, asset2])
    await db_session.flush()

    # Create holdings
    holding1 = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset1.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("1500.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("1755.00")
    )
    holding2 = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset2.id,
        quantity=Decimal("5"),
        average_cost=Decimal("2800.00"),
        cost_basis=Decimal("14000.00"),
        current_price=Decimal("2950.00"),
        current_value=Decimal("14750.00")
    )
    db_session.add_all([holding1, holding2])
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    total_value = await analytics_service.get_portfolio_total_value(portfolio.id)

    assert total_value == Decimal("16505.00")


@pytest.mark.asyncio
async def test_calculate_roi(db_session: AsyncSession):
    """Test ROI calculation"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(symbol="AAPL", name="Apple Inc.", type="stock", currency="USD")
    db_session.add(asset)
    await db_session.flush()

    # Create holding
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("1500.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("1755.00")
    )
    db_session.add(holding)
    await db_session.flush()

    # Create buy transaction
    transaction = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="buy",
        quantity=Decimal("10"),
        price=Decimal("150.00"),
        total_amount=Decimal("1500.00"),
        fee=Decimal("10.00"),
        tax=Decimal("0.00"),
        currency="USD",
        date=date(2024, 1, 1)
    )
    db_session.add(transaction)
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    roi_metrics = await analytics_service.calculate_roi(portfolio.id)

    assert roi_metrics["current_value"] == Decimal("1755.00")
    assert roi_metrics["total_invested"] == Decimal("1510.00")  # 1500 + 10 fee
    assert roi_metrics["total_withdrawn"] == Decimal("0")
    assert roi_metrics["net_invested"] == Decimal("1510.00")
    assert roi_metrics["absolute_gain_loss"] == Decimal("245.00")
    # ROI = (245 / 1510) * 100 = 16.225...%
    assert (
        roi_metrics["roi_percent"] > Decimal("16")
        and roi_metrics["roi_percent"] < Decimal("17")
    )


@pytest.mark.asyncio
async def test_calculate_roi_with_sales(db_session: AsyncSession):
    """Test ROI calculation with buy and sell transactions"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(symbol="AAPL", name="Apple Inc.", type="stock", currency="USD")
    db_session.add(asset)
    await db_session.flush()

    # Create holding (remaining 5 shares after selling 5)
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("5"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("750.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("877.50")
    )
    db_session.add(holding)
    await db_session.flush()

    # Create buy transaction (10 shares)
    buy_txn = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="buy",
        quantity=Decimal("10"),
        price=Decimal("150.00"),
        total_amount=Decimal("1500.00"),
        fee=Decimal("10.00"),
        tax=Decimal("0.00"),
        currency="USD",
        date=date(2024, 1, 1)
    )
    # Create sell transaction (5 shares)
    sell_txn = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="sell",
        quantity=Decimal("5"),
        price=Decimal("160.00"),
        total_amount=Decimal("800.00"),
        fee=Decimal("5.00"),
        tax=Decimal("0.00"),
        currency="USD",
        date=date(2024, 6, 1)
    )
    db_session.add_all([buy_txn, sell_txn])
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    roi_metrics = await analytics_service.calculate_roi(portfolio.id)

    # Net invested = 1510 (buy) - 795 (sell proceeds) = 715
    assert roi_metrics["net_invested"] == Decimal("715.00")
    # Current value = 877.50
    # Absolute gain = 877.50 - 715 = 162.50
    assert roi_metrics["absolute_gain_loss"] == Decimal("162.50")


@pytest.mark.asyncio
async def test_get_asset_allocation(db_session: AsyncSession):
    """Test asset allocation breakdown"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create assets with different classes
    asset1 = Asset(
        symbol="AAPL",
        name="Apple Inc.",
        type="stock",
        asset_class="equity",
        currency="USD"
    )
    asset2 = Asset(
        symbol="BTC",
        name="Bitcoin",
        type="crypto",
        asset_class="cryptocurrency",
        currency="USD"
    )
    asset3 = Asset(
        symbol="GOOGL",
        name="Alphabet Inc.",
        type="stock",
        asset_class="equity",
        currency="USD"
    )
    db_session.add_all([asset1, asset2, asset3])
    await db_session.flush()

    # Create holdings
    holding1 = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset1.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("1500.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("1755.00")
    )
    holding2 = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset2.id,
        quantity=Decimal("0.5"),
        average_cost=Decimal("40000.00"),
        cost_basis=Decimal("20000.00"),
        current_price=Decimal("45000.00"),
        current_value=Decimal("22500.00")
    )
    holding3 = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset3.id,
        quantity=Decimal("5"),
        average_cost=Decimal("2800.00"),
        cost_basis=Decimal("14000.00"),
        current_price=Decimal("2950.00"),
        current_value=Decimal("14750.00")
    )
    db_session.add_all([holding1, holding2, holding3])
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    allocation = await analytics_service.get_asset_allocation(portfolio.id)

    # Total value = 1755 + 22500 + 14750 = 39005
    assert allocation["total_value"] == Decimal("39005.00")

    # Check allocation by class
    by_class = {item["asset_class"]: item for item in allocation["by_class"]}
    assert "equity" in by_class
    assert "cryptocurrency" in by_class

    # Equity = 1755 + 14750 = 16505
    equity_value = by_class["equity"]["value"]
    assert equity_value == Decimal("16505.00")

    # Crypto = 22500
    crypto_value = by_class["cryptocurrency"]["value"]
    assert crypto_value == Decimal("22500.00")

    # Check allocation by type
    by_type = {item["asset_type"]: item for item in allocation["by_type"]}
    assert "stock" in by_type
    assert "crypto" in by_type

    # Check individual assets
    assert len(allocation["by_asset"]) == 3


@pytest.mark.asyncio
async def test_get_holdings_performance(db_session: AsyncSession):
    """Test holdings performance calculation"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(symbol="AAPL", name="Apple Inc.", type="stock", currency="USD")
    db_session.add(asset)
    await db_session.flush()

    # Create holding with gain
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("1500.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("1755.00")
    )
    db_session.add(holding)
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    holdings = await analytics_service.get_holdings_performance(portfolio.id)

    assert len(holdings) == 1
    h = holdings[0]
    assert h["symbol"] == "AAPL"
    assert h["quantity"] == Decimal("10")
    assert h["cost_basis"] == Decimal("1500.00")
    assert h["current_value"] == Decimal("1755.00")
    assert h["unrealized_gain_loss"] == Decimal("255.00")
    assert h["unrealized_gain_loss_percent"] == Decimal("17.00")


@pytest.mark.asyncio
async def test_get_dividend_metrics(db_session: AsyncSession):
    """Test dividend metrics calculation"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(symbol="AAPL", name="Apple Inc.", type="stock", currency="USD")
    db_session.add(asset)
    await db_session.flush()

    # Create holding
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("100"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("15000.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("17550.00")
    )
    db_session.add(holding)
    await db_session.flush()

    # Create dividend transactions
    div1 = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="dividend",
        quantity=Decimal("0"),
        price=Decimal("0.23"),
        total_amount=Decimal("23.00"),
        fee=Decimal("0.00"),
        tax=Decimal("3.00"),
        currency="USD",
        date=date(2024, 3, 15)
    )
    div2 = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="dividend",
        quantity=Decimal("0"),
        price=Decimal("0.24"),
        total_amount=Decimal("24.00"),
        fee=Decimal("0.00"),
        tax=Decimal("3.00"),
        currency="USD",
        date=date(2024, 6, 15)
    )
    div3 = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="dividend",
        quantity=Decimal("0"),
        price=Decimal("0.24"),
        total_amount=Decimal("24.00"),
        fee=Decimal("0.00"),
        tax=Decimal("3.00"),
        currency="USD",
        date=date(2024, 9, 15)
    )
    db_session.add_all([div1, div2, div3])
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    dividends = await analytics_service.get_dividend_metrics(
        portfolio.id,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )

    # Total dividends = 20 + 21 + 21 = 62 (after tax)
    assert dividends["total_dividends"] == Decimal("62.00")
    assert dividends["dividend_count"] == 3

    # Check history
    assert len(dividends["history"]) == 3

    # Check by asset
    assert len(dividends["by_asset"]) == 1
    assert dividends["by_asset"][0]["total_dividends"] == Decimal("62.00")
    assert dividends["by_asset"][0]["count"] == 3


@pytest.mark.asyncio
async def test_calculate_xirr_simple(db_session: AsyncSession):
    """Test XIRR calculation with simple investment"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(symbol="AAPL", name="Apple Inc.", type="stock", currency="USD")
    db_session.add(asset)
    await db_session.flush()

    # Create holding
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("10"),
        average_cost=Decimal("100.00"),
        cost_basis=Decimal("1000.00"),
        current_price=Decimal("150.00"),
        current_value=Decimal("1500.00")
    )
    db_session.add(holding)
    await db_session.flush()

    # Create buy transaction
    transaction = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="buy",
        quantity=Decimal("10"),
        price=Decimal("100.00"),
        total_amount=Decimal("1000.00"),
        fee=Decimal("0.00"),
        tax=Decimal("0.00"),
        currency="USD",
        date=date(2023, 1, 1)
    )
    db_session.add(transaction)
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    xirr = await analytics_service.calculate_xirr(portfolio.id, end_date=date(2024, 1, 1))

    # With $1000 invested becoming $1500 in 1 year, XIRR should be ~50%
    assert xirr is not None
    assert xirr > Decimal("40") and xirr < Decimal("60")


@pytest.mark.asyncio
async def test_calculate_twr_simple(db_session: AsyncSession):
    """Test TWR calculation with simple investment"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(symbol="AAPL", name="Apple Inc.", type="stock", currency="USD")
    db_session.add(asset)
    await db_session.flush()

    # Create holding
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("10"),
        average_cost=Decimal("100.00"),
        cost_basis=Decimal("1000.00"),
        current_price=Decimal("150.00"),
        current_value=Decimal("1500.00")
    )
    db_session.add(holding)
    await db_session.flush()

    # Create buy transaction
    transaction = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="buy",
        quantity=Decimal("10"),
        price=Decimal("100.00"),
        total_amount=Decimal("1000.00"),
        fee=Decimal("0.00"),
        tax=Decimal("0.00"),
        currency="USD",
        date=date(2023, 1, 1)
    )
    db_session.add(transaction)
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    twr = await analytics_service.calculate_twr(portfolio.id)

    # TWR = ((1500 / 1000) - 1) * 100 = 50%
    assert twr is not None
    assert twr == Decimal("50.00")


@pytest.mark.asyncio
async def test_comprehensive_analytics(db_session: AsyncSession):
    """Test comprehensive analytics"""
    # Create portfolio
    portfolio = Portfolio(
        user_id=TEST_USER_ID, name="Test Portfolio", currency="USD"
    )
    db_session.add(portfolio)
    await db_session.flush()

    # Create asset
    asset = Asset(
        symbol="AAPL",
        name="Apple Inc.",
        type="stock",
        asset_class="equity",
        currency="USD"
    )
    db_session.add(asset)
    await db_session.flush()

    # Create holding
    holding = Holding(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        quantity=Decimal("10"),
        average_cost=Decimal("150.00"),
        cost_basis=Decimal("1500.00"),
        current_price=Decimal("175.50"),
        current_value=Decimal("1755.00")
    )
    db_session.add(holding)
    await db_session.flush()

    # Create buy transaction
    transaction = PortfolioTransaction(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        type="buy",
        quantity=Decimal("10"),
        price=Decimal("150.00"),
        total_amount=Decimal("1500.00"),
        fee=Decimal("10.00"),
        tax=Decimal("0.00"),
        currency="USD",
        date=date(2024, 1, 1)
    )
    db_session.add(transaction)
    await db_session.commit()

    analytics_service = AnalyticsService(db_session)
    analytics = await analytics_service.get_comprehensive_analytics(portfolio.id)

    # Verify all sections are present
    assert analytics["portfolio_id"] == portfolio.id
    assert analytics["portfolio_name"] == "Test Portfolio"
    assert analytics["currency"] == "USD"
    assert analytics["total_value"] == Decimal("1755.00")
    assert "roi" in analytics
    assert "allocation" in analytics
    assert "holdings" in analytics
    assert "dividends" in analytics
    assert "last_updated" in analytics

    # Verify ROI
    assert analytics["roi"]["current_value"] == Decimal("1755.00")

    # Verify allocation
    assert analytics["allocation"]["total_value"] == Decimal("1755.00")
    assert len(analytics["allocation"]["by_asset"]) == 1

    # Verify holdings
    assert len(analytics["holdings"]) == 1
