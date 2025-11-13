"""
Accounts API endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.account import Account
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountBalance,
    AccountList,
)

router = APIRouter()


@router.get("/", response_model=AccountList)
async def list_accounts(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all accounts for the current user.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **is_active**: Filter by active status (optional)
    - **account_type**: Filter by account type (optional)
    """
    # Build query filters
    filters = [Account.user_id == current_user.id, Account.deleted_at.is_(None)]

    if is_active is not None:
        filters.append(Account.is_active == is_active)

    if account_type:
        filters.append(Account.type == account_type)

    # Get total count
    count_query = select(Account).filter(and_(*filters))
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Get accounts with pagination
    query = (
        select(Account)
        .filter(and_(*filters))
        .order_by(Account.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    accounts = result.scalars().all()

    return AccountList(total=total, accounts=accounts)


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new account for the current user.

    - **name**: Account name (required)
    - **type**: Account type (required)
    - **currency**: Currency code (default: USD)
    - **initial_balance**: Initial balance (default: 0.00)
    - **account_number**: Account number (optional)
    - **institution**: Financial institution name (optional)
    - **color**: Color in hex format (optional)
    - **icon**: Icon name (optional)
    - **is_active**: Whether account is active (default: true)
    - **include_in_net_worth**: Include in net worth calculations (default: true)
    - **notes**: Additional notes (optional)
    """
    # Create account instance
    account = Account(
        user_id=current_user.id,
        name=account_data.name,
        type=account_data.type,
        currency=account_data.currency,
        initial_balance=account_data.initial_balance,
        current_balance=account_data.initial_balance,  # Set current balance to initial
        account_number=account_data.account_number,
        institution=account_data.institution,
        color=account_data.color,
        icon=account_data.icon,
        is_active=account_data.is_active,
        include_in_net_worth=account_data.include_in_net_worth,
        notes=account_data.notes,
    )

    db.add(account)
    await db.commit()
    await db.refresh(account)

    return account


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get account details by ID.

    Returns the account details if it belongs to the current user.
    """
    query = select(Account).filter(
        and_(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )

    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing account.

    Updates only the fields provided in the request body.
    """
    # Get the account
    query = select(Account).filter(
        and_(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )

    # Update fields that were provided
    update_data = account_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)

    account.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(account)

    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete an account (soft delete).

    This performs a soft delete by setting the deleted_at timestamp.
    The account will no longer appear in list queries but remains in the database.
    """
    # Get the account
    query = select(Account).filter(
        and_(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )

    # Soft delete by setting deleted_at timestamp
    account.deleted_at = datetime.utcnow()

    await db.commit()

    return None


@router.get("/{account_id}/balance", response_model=AccountBalance)
async def get_account_balance(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the current balance for a specific account.

    Returns detailed balance information including:
    - Current balance
    - Initial balance
    - Balance change from initial
    - Last update timestamp
    """
    # Get the account
    query = select(Account).filter(
        and_(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found",
        )

    # Calculate balance change
    balance_change = account.current_balance - account.initial_balance

    return AccountBalance(
        account_id=account.id,
        uuid=account.uuid,
        name=account.name,
        currency=account.currency,
        current_balance=account.current_balance,
        initial_balance=account.initial_balance,
        balance_change=balance_change,
        last_updated=account.updated_at,
    )
