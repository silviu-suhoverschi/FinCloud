"""
Holdings API endpoints
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.models.asset import Asset
from app.schemas.holding import (
    HoldingCreate,
    HoldingUpdate,
    HoldingResponse,
    HoldingList,
)

router = APIRouter()


@router.get("/", response_model=HoldingList)
async def list_holdings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    portfolio_id: Optional[int] = Query(
        None, description="Filter by portfolio ID (optional)"
    ),
    asset_id: Optional[int] = Query(None, description="Filter by asset ID (optional)"),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    List all holdings for the current user.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **portfolio_id**: Filter by portfolio ID (optional)
    - **asset_id**: Filter by asset ID (optional)
    """
    # Build query filters - ensure user owns the portfolio
    filters = [
        Holding.deleted_at.is_(None),
        Portfolio.user_id == user_id,
        Portfolio.deleted_at.is_(None),
    ]

    if portfolio_id is not None:
        filters.append(Holding.portfolio_id == portfolio_id)

    if asset_id is not None:
        filters.append(Holding.asset_id == asset_id)

    # Get total count
    count_query = (
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .filter(and_(*filters))
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Get holdings with pagination
    query = (
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .filter(and_(*filters))
        .order_by(Holding.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    holdings = result.scalars().all()

    return HoldingList(total=total, holdings=holdings)


@router.post("/", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def create_holding(
    holding_data: HoldingCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new holding for a portfolio.

    - **portfolio_id**: Portfolio ID (required)
    - **asset_id**: Asset ID (required)
    - **quantity**: Quantity of the asset (required)
    - **average_cost**: Average cost per unit (default: 0)
    - **notes**: Additional notes (optional)
    """
    # Verify the portfolio exists and belongs to the user
    portfolio_query = select(Portfolio).filter(
        and_(
            Portfolio.id == holding_data.portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    portfolio_result = await db.execute(portfolio_query)
    portfolio = portfolio_result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {holding_data.portfolio_id} not found",
        )

    # Verify the asset exists
    asset_query = select(Asset).filter(
        and_(
            Asset.id == holding_data.asset_id,
            Asset.deleted_at.is_(None),
        )
    )
    asset_result = await db.execute(asset_query)
    asset = asset_result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with ID {holding_data.asset_id} not found",
        )

    # Check if holding already exists (unique constraint: portfolio_id + asset_id)
    existing_query = select(Holding).filter(
        and_(
            Holding.portfolio_id == holding_data.portfolio_id,
            Holding.asset_id == holding_data.asset_id,
            Holding.deleted_at.is_(None),
        )
    )
    existing_result = await db.execute(existing_query)
    existing_holding = existing_result.scalar_one_or_none()

    if existing_holding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Holding for asset '{asset.symbol}' already exists in this portfolio. Use PUT to update it.",
        )

    # Calculate cost basis
    cost_basis = holding_data.quantity * holding_data.average_cost

    # Create holding instance
    holding = Holding(
        portfolio_id=holding_data.portfolio_id,
        asset_id=holding_data.asset_id,
        quantity=holding_data.quantity,
        average_cost=holding_data.average_cost,
        cost_basis=cost_basis,
        notes=holding_data.notes,
    )

    db.add(holding)
    await db.commit()
    await db.refresh(holding)

    return holding


@router.get("/{holding_id}", response_model=HoldingResponse)
async def get_holding(
    holding_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get holding details by ID.

    Returns the holding details if it belongs to a portfolio owned by the current user.
    """
    query = (
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .filter(
            and_(
                Holding.id == holding_id,
                Portfolio.user_id == user_id,
                Holding.deleted_at.is_(None),
                Portfolio.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with ID {holding_id} not found",
        )

    return holding


@router.put("/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: int,
    holding_data: HoldingUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update an existing holding.

    Updates only the fields provided in the request body.
    Cost basis is automatically recalculated if quantity or average_cost changes.
    """
    # Get the holding and verify ownership through portfolio
    query = (
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .filter(
            and_(
                Holding.id == holding_id,
                Portfolio.user_id == user_id,
                Holding.deleted_at.is_(None),
                Portfolio.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with ID {holding_id} not found",
        )

    # Update fields that were provided
    update_data = holding_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(holding, field, value)

    # Recalculate cost basis if quantity or average_cost changed
    if "quantity" in update_data or "average_cost" in update_data:
        holding.cost_basis = holding.quantity * holding.average_cost

    holding.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(holding)

    return holding


@router.delete("/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    holding_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a holding (soft delete).

    This performs a soft delete by setting the deleted_at timestamp.
    The holding will no longer appear in list queries but remains in the database.
    """
    # Get the holding and verify ownership through portfolio
    query = (
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .filter(
            and_(
                Holding.id == holding_id,
                Portfolio.user_id == user_id,
                Holding.deleted_at.is_(None),
                Portfolio.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    holding = result.scalar_one_or_none()

    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Holding with ID {holding_id} not found",
        )

    # Soft delete the holding
    holding.deleted_at = datetime.utcnow()

    await db.commit()

    return None
