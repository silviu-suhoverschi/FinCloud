"""
Tests for database models
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio


@pytest.mark.asyncio
async def test_create_portfolio(db_session: AsyncSession):
    """Test creating a portfolio"""
    portfolio = Portfolio(
        user_id=1, name="Test Portfolio", description="A test portfolio", currency="USD"
    )

    db_session.add(portfolio)
    await db_session.commit()
    await db_session.refresh(portfolio)

    assert portfolio.id is not None
    assert portfolio.uuid is not None
    assert portfolio.user_id == 1
    assert portfolio.name == "Test Portfolio"
    assert portfolio.description == "A test portfolio"
    assert portfolio.currency == "USD"
    assert portfolio.is_active is True
    assert portfolio.sort_order == 0
    assert portfolio.created_at is not None
    assert portfolio.updated_at is not None
    assert portfolio.deleted_at is None


@pytest.mark.asyncio
async def test_portfolio_unique_constraint(db_session: AsyncSession):
    """Test that user_id + name combination must be unique"""
    portfolio1 = Portfolio(user_id=1, name="Unique Portfolio", currency="USD")
    db_session.add(portfolio1)
    await db_session.commit()

    # Try to create another portfolio with the same user_id and name
    portfolio2 = Portfolio(user_id=1, name="Unique Portfolio", currency="EUR")
    db_session.add(portfolio2)

    with pytest.raises(Exception):  # Should raise an IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_portfolio_repr(db_session: AsyncSession):
    """Test portfolio string representation"""
    portfolio = Portfolio(user_id=1, name="Test Portfolio", currency="USD")

    db_session.add(portfolio)
    await db_session.commit()
    await db_session.refresh(portfolio)

    repr_str = repr(portfolio)
    assert "Portfolio" in repr_str
    assert str(portfolio.id) in repr_str
    assert "Test Portfolio" in repr_str


@pytest.mark.asyncio
async def test_query_portfolio(db_session: AsyncSession):
    """Test querying portfolios"""
    # Create test portfolios
    portfolio1 = Portfolio(user_id=1, name="Portfolio 1", currency="USD")
    portfolio2 = Portfolio(user_id=1, name="Portfolio 2", currency="EUR")
    portfolio3 = Portfolio(user_id=2, name="Portfolio 3", currency="USD")

    db_session.add_all([portfolio1, portfolio2, portfolio3])
    await db_session.commit()

    # Query portfolios for user 1
    result = await db_session.execute(select(Portfolio).where(Portfolio.user_id == 1))
    user1_portfolios = result.scalars().all()

    assert len(user1_portfolios) == 2
    assert all(p.user_id == 1 for p in user1_portfolios)
