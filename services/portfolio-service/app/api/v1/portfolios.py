"""
Portfolios API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.portfolio import Portfolio
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioUpdate,
    PortfolioResponse,
    PortfolioList,
)

router = APIRouter()


@router.get("/", response_model=PortfolioList)
async def list_portfolios(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    List all portfolios for the current user.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status (optional)
    """
    # Build query filters
    filters = [Portfolio.user_id == user_id, Portfolio.deleted_at.is_(None)]

    if is_active is not None:
        filters.append(Portfolio.is_active == is_active)

    # Get total count
    count_query = select(Portfolio).filter(and_(*filters))
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Get portfolios with pagination
    query = (
        select(Portfolio)
        .filter(and_(*filters))
        .order_by(Portfolio.sort_order.asc(), Portfolio.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    portfolios = result.scalars().all()

    return PortfolioList(total=total, portfolios=portfolios)


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new portfolio for the current user.

    - **name**: Portfolio name (required)
    - **description**: Portfolio description (optional)
    - **currency**: Currency code (default: USD)
    - **is_active**: Whether portfolio is active (default: true)
    - **sort_order**: Sort order for display (default: 0)
    """
    # Check for duplicate portfolio name for this user
    existing_query = select(Portfolio).filter(
        and_(
            Portfolio.user_id == user_id,
            Portfolio.name == portfolio_data.name,
            Portfolio.deleted_at.is_(None),
        )
    )
    existing_result = await db.execute(existing_query)
    existing_portfolio = existing_result.scalar_one_or_none()

    if existing_portfolio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Portfolio with name '{portfolio_data.name}' already exists",
        )

    # Create portfolio instance
    portfolio = Portfolio(
        user_id=user_id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        currency=portfolio_data.currency,
        is_active=portfolio_data.is_active,
        sort_order=portfolio_data.sort_order,
    )

    db.add(portfolio)
    await db.commit()
    await db.refresh(portfolio)

    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get portfolio details by ID.

    Returns the portfolio details if it belongs to the current user.
    """
    query = select(Portfolio).filter(
        and_(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {portfolio_id} not found",
        )

    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update an existing portfolio.

    Updates only the fields provided in the request body.
    """
    # Get the portfolio
    query = select(Portfolio).filter(
        and_(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {portfolio_id} not found",
        )

    # If name is being updated, check for duplicates
    if portfolio_data.name and portfolio_data.name != portfolio.name:
        duplicate_query = select(Portfolio).filter(
            and_(
                Portfolio.user_id == user_id,
                Portfolio.name == portfolio_data.name,
                Portfolio.id != portfolio_id,
                Portfolio.deleted_at.is_(None),
            )
        )
        duplicate_result = await db.execute(duplicate_query)
        duplicate_portfolio = duplicate_result.scalar_one_or_none()

        if duplicate_portfolio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Portfolio with name '{portfolio_data.name}' already exists",
            )

    # Update fields that were provided
    update_data = portfolio_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)

    portfolio.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(portfolio)

    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a portfolio (soft delete).

    This performs a soft delete by setting the deleted_at timestamp.
    The portfolio will no longer appear in list queries but remains in the database.
    All associated holdings and transactions are also soft-deleted.
    """
    # Get the portfolio
    query = select(Portfolio).filter(
        and_(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {portfolio_id} not found",
        )

    # Soft delete the portfolio
    portfolio.deleted_at = datetime.utcnow()

    await db.commit()

    return None
