"""
Budgets API endpoints
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.budget import Budget
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetWithSpending,
    BudgetList,
    BudgetProgress,
    BudgetPeriod,
)
from app.services.budget_service import BudgetService

router = APIRouter()


@router.get("/", response_model=BudgetList)
async def list_budgets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Max number of records to return"
    ),
    period: Optional[BudgetPeriod] = Query(None, description="Filter by budget period"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all budgets for the current user with optional filters.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **period**: Filter by budget period (daily, weekly, monthly, quarterly, yearly, custom)
    - **is_active**: Filter by active status
    - **category_id**: Filter by category ID
    - **account_id**: Filter by account ID
    """
    # Build query filters
    filters = [Budget.user_id == current_user.id, Budget.deleted_at.is_(None)]

    if period is not None:
        filters.append(Budget.period == period.value)

    if is_active is not None:
        filters.append(Budget.is_active == is_active)

    if category_id is not None:
        filters.append(Budget.category_id == category_id)

    if account_id is not None:
        filters.append(Budget.account_id == account_id)

    # Get total count
    count_query = select(func.count()).select_from(Budget).filter(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    # Get budgets with pagination and eagerly load category relationship
    query = (
        select(Budget)
        .options(selectinload(Budget.category))
        .filter(and_(*filters))
        .order_by(Budget.start_date.desc(), Budget.name)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    budgets = result.scalars().all()

    return BudgetList(total=total, budgets=budgets)


@router.get("/{budget_id}", response_model=BudgetWithSpending)
async def get_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific budget by ID with spending information.

    - **budget_id**: Budget ID
    """
    # Get budget and eagerly load category relationship
    query = (
        select(Budget)
        .options(selectinload(Budget.category))
        .filter(
            and_(
                Budget.id == budget_id,
                Budget.user_id == current_user.id,
                Budget.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )

    # Calculate spending
    spending_info = await BudgetService.calculate_budget_spending(db, budget)

    # Convert budget to dict and add spending info
    budget_dict = {
        "id": budget.id,
        "uuid": budget.uuid,
        "user_id": budget.user_id,
        "category_id": budget.category_id,
        "account_id": budget.account_id,
        "name": budget.name,
        "amount": budget.amount,
        "currency": budget.currency,
        "period": budget.period,
        "start_date": budget.start_date,
        "end_date": budget.end_date,
        "rollover_unused": budget.rollover_unused,
        "alert_enabled": budget.alert_enabled,
        "alert_threshold": budget.alert_threshold,
        "is_active": budget.is_active,
        "created_at": budget.created_at,
        "updated_at": budget.updated_at,
        "deleted_at": budget.deleted_at,
        **spending_info,
    }

    return BudgetWithSpending(**budget_dict)


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_data: BudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new budget for the current user.

    - **name**: Budget name (required)
    - **amount**: Budget amount (required, must be positive)
    - **currency**: Currency code (default: USD)
    - **period**: Budget period - daily, weekly, monthly, quarterly, yearly, custom (required)
    - **start_date**: Budget start date (required)
    - **end_date**: Budget end date (optional, required for custom period)
    - **category_id**: Category ID (required if account_id not provided)
    - **account_id**: Account ID (required if category_id not provided)
    - **rollover_unused**: Whether to rollover unused budget (optional, default: false)
    - **alert_enabled**: Enable budget alerts (optional, default: true)
    - **alert_threshold**: Alert threshold percentage (optional, default: 80.00)
    - **is_active**: Whether budget is active (optional, default: true)
    """
    # Validate budget data
    try:
        await BudgetService.validate_budget_data(
            db,
            current_user.id,
            budget_data.category_id,
            budget_data.account_id,
            budget_data.start_date,
            budget_data.end_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Create new budget
    new_budget = Budget(
        user_id=current_user.id,
        name=budget_data.name,
        amount=budget_data.amount,
        currency=budget_data.currency,
        period=budget_data.period.value,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        category_id=budget_data.category_id,
        account_id=budget_data.account_id,
        rollover_unused=budget_data.rollover_unused,
        alert_enabled=budget_data.alert_enabled,
        alert_threshold=budget_data.alert_threshold,
        is_active=budget_data.is_active,
    )

    db.add(new_budget)
    await db.commit()
    await db.refresh(new_budget)

    return new_budget


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing budget.

    - **budget_id**: Budget ID
    - **name**: Budget name (optional)
    - **amount**: Budget amount (optional)
    - **currency**: Currency code (optional)
    - **period**: Budget period (optional)
    - **start_date**: Budget start date (optional)
    - **end_date**: Budget end date (optional)
    - **category_id**: Category ID (optional)
    - **account_id**: Account ID (optional)
    - **rollover_unused**: Rollover unused budget (optional)
    - **alert_enabled**: Enable alerts (optional)
    - **alert_threshold**: Alert threshold (optional)
    - **is_active**: Active status (optional)
    """
    # Get existing budget
    query = select(Budget).filter(
        and_(
            Budget.id == budget_id,
            Budget.user_id == current_user.id,
            Budget.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )

    # Validate if category_id, account_id, or dates are being changed
    if (
        budget_data.category_id is not None
        or budget_data.account_id is not None
        or budget_data.start_date is not None
        or budget_data.end_date is not None
    ):
        try:
            await BudgetService.validate_budget_data(
                db,
                current_user.id,
                (
                    budget_data.category_id
                    if budget_data.category_id is not None
                    else budget.category_id
                ),
                (
                    budget_data.account_id
                    if budget_data.account_id is not None
                    else budget.account_id
                ),
                (
                    budget_data.start_date
                    if budget_data.start_date is not None
                    else budget.start_date
                ),
                (
                    budget_data.end_date
                    if budget_data.end_date is not None
                    else budget.end_date
                ),
                budget_id=budget_id,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Update fields
    if budget_data.name is not None:
        budget.name = budget_data.name
    if budget_data.amount is not None:
        budget.amount = budget_data.amount
    if budget_data.currency is not None:
        budget.currency = budget_data.currency
    if budget_data.period is not None:
        budget.period = budget_data.period.value
    if budget_data.start_date is not None:
        budget.start_date = budget_data.start_date
    if budget_data.end_date is not None:
        budget.end_date = budget_data.end_date
    if budget_data.category_id is not None:
        budget.category_id = budget_data.category_id
    if budget_data.account_id is not None:
        budget.account_id = budget_data.account_id
    if budget_data.rollover_unused is not None:
        budget.rollover_unused = budget_data.rollover_unused
    if budget_data.alert_enabled is not None:
        budget.alert_enabled = budget_data.alert_enabled
    if budget_data.alert_threshold is not None:
        budget.alert_threshold = budget_data.alert_threshold
    if budget_data.is_active is not None:
        budget.is_active = budget_data.is_active

    budget.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(budget)

    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_200_OK)
async def delete_budget(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a budget (soft delete).

    - **budget_id**: Budget ID
    """
    # Get existing budget
    query = select(Budget).filter(
        and_(
            Budget.id == budget_id,
            Budget.user_id == current_user.id,
            Budget.deleted_at.is_(None),
        )
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )

    # Soft delete the budget
    budget.deleted_at = datetime.utcnow()

    await db.commit()

    return {
        "message": f"Successfully deleted budget '{budget.name}'",
        "budget_id": budget_id,
    }


@router.get("/{budget_id}/progress", response_model=BudgetProgress)
async def get_budget_progress(
    budget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed progress information for a budget.

    Returns spending progress, percentage used, alerts, and days remaining.

    - **budget_id**: Budget ID
    """
    # Get budget and eagerly load category relationship
    query = (
        select(Budget)
        .options(selectinload(Budget.category))
        .filter(
            and_(
                Budget.id == budget_id,
                Budget.user_id == current_user.id,
                Budget.deleted_at.is_(None),
            )
        )
    )
    result = await db.execute(query)
    budget = result.scalar_one_or_none()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with ID {budget_id} not found",
        )

    # Get progress information
    progress_info = await BudgetService.get_budget_progress(db, budget)

    return BudgetProgress(**progress_info)
