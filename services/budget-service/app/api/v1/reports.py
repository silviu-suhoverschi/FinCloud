"""
Reports and Analytics API endpoints.
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.reports import (
    CashflowReport,
    SpendingReport,
    IncomeReport,
    NetWorthReport,
)
from app.services.reports_service import ReportsService

router = APIRouter()


@router.get("/cashflow", response_model=CashflowReport)
async def get_cashflow_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    currency: Optional[str] = Query(
        None, min_length=3, max_length=3, description="Currency filter (optional)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get monthly cashflow report.

    Returns income, expenses, and net cashflow for each month in the date range.

    **Parameters:**
    - **start_date**: Start date for the report (YYYY-MM-DD)
    - **end_date**: End date for the report (YYYY-MM-DD)
    - **currency**: Optional currency filter (e.g., USD, EUR)

    **Returns:**
    - Monthly breakdown of income, expenses, and net cashflow
    - Total income, expenses, and net cashflow for the period
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Validate currency format
    if currency and len(currency) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code must be exactly 3 characters",
        )

    try:
        report_data = await ReportsService.generate_cashflow_report(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
        )
        return CashflowReport(**report_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cashflow report: {str(e)}",
        )


@router.get("/spending", response_model=SpendingReport)
async def get_spending_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    currency: Optional[str] = Query(
        None, min_length=3, max_length=3, description="Currency filter (optional)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get spending analysis by category.

    Returns total spending broken down by category with percentages.

    **Parameters:**
    - **start_date**: Start date for the report (YYYY-MM-DD)
    - **end_date**: End date for the report (YYYY-MM-DD)
    - **currency**: Optional currency filter (e.g., USD, EUR)

    **Returns:**
    - Spending breakdown by category with amounts and percentages
    - Total spending and transaction count for the period
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Validate currency format
    if currency and len(currency) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code must be exactly 3 characters",
        )

    try:
        report_data = await ReportsService.generate_spending_report(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
        )
        return SpendingReport(**report_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating spending report: {str(e)}",
        )


@router.get("/income", response_model=IncomeReport)
async def get_income_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    currency: Optional[str] = Query(
        None, min_length=3, max_length=3, description="Currency filter (optional)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get income analysis report.

    Returns total income broken down by category with percentages and monthly averages.

    **Parameters:**
    - **start_date**: Start date for the report (YYYY-MM-DD)
    - **end_date**: End date for the report (YYYY-MM-DD)
    - **currency**: Optional currency filter (e.g., USD, EUR)

    **Returns:**
    - Income breakdown by source category with amounts and percentages
    - Total income, transaction count, and average monthly income
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Validate currency format
    if currency and len(currency) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code must be exactly 3 characters",
        )

    try:
        report_data = await ReportsService.generate_income_report(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
        )
        return IncomeReport(**report_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating income report: {str(e)}",
        )


@router.get("/net-worth", response_model=NetWorthReport)
async def get_net_worth_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    currency: Optional[str] = Query(
        None, min_length=3, max_length=3, description="Currency filter (optional)"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get net worth timeline report.

    Returns net worth over time with monthly snapshots showing assets, liabilities,
    and net worth calculations.

    **Parameters:**
    - **start_date**: Start date for the report (YYYY-MM-DD)
    - **end_date**: End date for the report (YYYY-MM-DD)
    - **currency**: Optional currency filter (e.g., USD, EUR)

    **Returns:**
    - Monthly timeline of net worth, assets, and liabilities
    - Current net worth with change and percentage change
    - Current account balances
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )

    # Validate currency format
    if currency and len(currency) != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currency code must be exactly 3 characters",
        )

    try:
        report_data = await ReportsService.generate_net_worth_report(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
        )
        return NetWorthReport(**report_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating net worth report: {str(e)}",
        )
