"""
Portfolio Transactions API endpoints
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.auth import get_current_user_id
from app.models.portfolio_transaction import PortfolioTransaction
from app.models.portfolio import Portfolio
from app.models.asset import Asset
from app.models.holding import Holding
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
    TransactionType,
)

router = APIRouter()


@router.get("/", response_model=TransactionList)
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    portfolio_id: Optional[int] = Query(
        None, description="Filter by portfolio ID (optional)"
    ),
    asset_id: Optional[int] = Query(None, description="Filter by asset ID (optional)"),
    transaction_type: Optional[TransactionType] = Query(
        None, description="Filter by transaction type (optional)"
    ),
    date_from: Optional[str] = Query(
        None, description="Filter transactions from this date (YYYY-MM-DD)"
    ),
    date_to: Optional[str] = Query(
        None, description="Filter transactions to this date (YYYY-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    List all portfolio transactions for the current user.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **portfolio_id**: Filter by portfolio ID (optional)
    - **asset_id**: Filter by asset ID (optional)
    - **transaction_type**: Filter by transaction type (optional)
    - **date_from**: Filter transactions from this date (optional)
    - **date_to**: Filter transactions to this date (optional)
    """
    # Build query filters - ensure user owns the portfolio
    filters = [
        PortfolioTransaction.deleted_at.is_(None),
        Portfolio.user_id == user_id,
        Portfolio.deleted_at.is_(None),
    ]

    if portfolio_id is not None:
        filters.append(PortfolioTransaction.portfolio_id == portfolio_id)

    if asset_id is not None:
        filters.append(PortfolioTransaction.asset_id == asset_id)

    if transaction_type is not None:
        filters.append(PortfolioTransaction.type == transaction_type.value)

    if date_from is not None:
        filters.append(PortfolioTransaction.date >= date_from)

    if date_to is not None:
        filters.append(PortfolioTransaction.date <= date_to)

    # Get total count
    count_query = (
        select(PortfolioTransaction)
        .join(Portfolio, PortfolioTransaction.portfolio_id == Portfolio.id)
        .filter(and_(*filters))
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Get transactions with pagination
    query = (
        select(PortfolioTransaction)
        .join(Portfolio, PortfolioTransaction.portfolio_id == Portfolio.id)
        .filter(and_(*filters))
        .order_by(
            PortfolioTransaction.date.desc(), PortfolioTransaction.created_at.desc()
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    transactions = result.scalars().all()

    return TransactionList(total=total, transactions=transactions)


@router.post(
    "/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
async def create_transaction(
    transaction_data: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new portfolio transaction (buy/sell/dividend/split).

    - **portfolio_id**: Portfolio ID (required)
    - **asset_id**: Asset ID (required)
    - **type**: Transaction type (BUY, SELL, DIVIDEND, SPLIT, etc.)
    - **quantity**: Quantity of the asset (required)
    - **price**: Price per unit (required)
    - **total_amount**: Total transaction amount (required)
    - **fee**: Transaction fee (default: 0)
    - **tax**: Transaction tax (default: 0)
    - **currency**: Currency code (default: USD)
    - **exchange_rate**: Exchange rate to base currency (default: 1.0)
    - **date**: Transaction date (required)
    - **notes**: Additional notes (optional)
    - **reference_number**: Reference/confirmation number (optional)
    """
    # Verify the portfolio exists and belongs to the user
    portfolio_query = select(Portfolio).filter(
        and_(
            Portfolio.id == transaction_data.portfolio_id,
            Portfolio.user_id == user_id,
            Portfolio.deleted_at.is_(None),
        )
    )
    portfolio_result = await db.execute(portfolio_query)
    portfolio = portfolio_result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with ID {transaction_data.portfolio_id} not found",
        )

    # Verify the asset exists
    asset_query = select(Asset).filter(
        and_(
            Asset.id == transaction_data.asset_id,
            Asset.deleted_at.is_(None),
        )
    )
    asset_result = await db.execute(asset_query)
    asset = asset_result.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset with ID {transaction_data.asset_id} not found",
        )

    # Create transaction instance
    transaction = PortfolioTransaction(
        portfolio_id=transaction_data.portfolio_id,
        asset_id=transaction_data.asset_id,
        type=transaction_data.type.value,
        quantity=transaction_data.quantity,
        price=transaction_data.price,
        total_amount=transaction_data.total_amount,
        fee=transaction_data.fee,
        tax=transaction_data.tax,
        currency=transaction_data.currency,
        exchange_rate=transaction_data.exchange_rate,
        date=transaction_data.date,
        notes=transaction_data.notes,
        reference_number=transaction_data.reference_number,
    )

    db.add(transaction)

    # Update or create holding for BUY/SELL transactions
    if transaction_data.type in [TransactionType.BUY, TransactionType.SELL]:
        await _update_holding(
            db,
            transaction_data.portfolio_id,
            transaction_data.asset_id,
            transaction_data.type,
            transaction_data.quantity,
            transaction_data.price,
            transaction_data.fee,
            transaction_data.tax,
        )

    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Get transaction details by ID.

    Returns the transaction details if it belongs to a portfolio owned by the current user.
    """
    query = (
        select(PortfolioTransaction)
        .join(Portfolio, PortfolioTransaction.portfolio_id == Portfolio.id)
        .filter(
            and_(
                PortfolioTransaction.id == transaction_id,
                Portfolio.user_id == user_id,
                PortfolioTransaction.deleted_at.is_(None),
                Portfolio.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update an existing portfolio transaction.

    Updates only the fields provided in the request body.
    """
    # Get the transaction and verify ownership through portfolio
    query = (
        select(PortfolioTransaction)
        .join(Portfolio, PortfolioTransaction.portfolio_id == Portfolio.id)
        .filter(
            and_(
                PortfolioTransaction.id == transaction_id,
                Portfolio.user_id == user_id,
                PortfolioTransaction.deleted_at.is_(None),
                Portfolio.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    # Update fields that were provided
    update_data = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "type" and value is not None:
            setattr(transaction, field, value.value)
        else:
            setattr(transaction, field, value)

    transaction.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(transaction)

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a transaction (soft delete).

    This performs a soft delete by setting the deleted_at timestamp.
    The transaction will no longer appear in list queries but remains in the database.
    """
    # Get the transaction and verify ownership through portfolio
    query = (
        select(PortfolioTransaction)
        .join(Portfolio, PortfolioTransaction.portfolio_id == Portfolio.id)
        .filter(
            and_(
                PortfolioTransaction.id == transaction_id,
                Portfolio.user_id == user_id,
                PortfolioTransaction.deleted_at.is_(None),
                Portfolio.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    transaction = result.scalar_one_or_none()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )

    # Soft delete the transaction
    transaction.deleted_at = datetime.utcnow()

    await db.commit()

    return None


async def _update_holding(
    db: AsyncSession,
    portfolio_id: int,
    asset_id: int,
    transaction_type: TransactionType,
    quantity: float,
    price: float,
    fee: float,
    tax: float,
):
    """
    Update or create holding based on buy/sell transaction.

    This is a helper function that adjusts holdings when transactions are recorded.
    """
    # Find existing holding
    holding_query = select(Holding).filter(
        and_(
            Holding.portfolio_id == portfolio_id,
            Holding.asset_id == asset_id,
            Holding.deleted_at.is_(None),
        )
    )
    result = await db.execute(holding_query)
    holding = result.scalar_one_or_none()

    if transaction_type == TransactionType.BUY:
        if holding:
            # Update existing holding
            total_cost = (
                (holding.quantity * holding.average_cost)
                + (quantity * price)
                + fee
                + tax
            )
            new_quantity = holding.quantity + quantity
            holding.average_cost = total_cost / new_quantity if new_quantity > 0 else 0
            holding.quantity = new_quantity
            holding.cost_basis = total_cost
            holding.updated_at = datetime.utcnow()
        else:
            # Create new holding
            cost_basis = (quantity * price) + fee + tax
            average_cost = cost_basis / quantity if quantity > 0 else 0
            new_holding = Holding(
                portfolio_id=portfolio_id,
                asset_id=asset_id,
                quantity=quantity,
                average_cost=average_cost,
                cost_basis=cost_basis,
            )
            db.add(new_holding)

    elif transaction_type == TransactionType.SELL:
        if holding:
            # Reduce holding quantity
            new_quantity = holding.quantity - quantity
            if new_quantity < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot sell {quantity} units. Only {holding.quantity} units available.",
                )
            holding.quantity = new_quantity
            holding.cost_basis = new_quantity * holding.average_cost
            holding.updated_at = datetime.utcnow()

            # If quantity becomes zero, soft delete the holding
            if new_quantity == 0:
                holding.deleted_at = datetime.utcnow()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot sell asset. No holding found for this asset in the portfolio.",
            )
