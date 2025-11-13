"""
Pydantic schemas for reports and analytics.
"""

from __future__ import annotations

from datetime import date as DateType
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class DateRangeParams(BaseModel):
    """Query parameters for date range filtering."""

    start_date: DateType = Field(..., description="Start date for the report")
    end_date: DateType = Field(..., description="End date for the report")
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency filter (optional)"
    )


class CashflowDataPoint(BaseModel):
    """Single month cashflow data point."""

    month: str = Field(..., description="Month in YYYY-MM format")
    income: Decimal = Field(..., description="Total income for the month")
    expenses: Decimal = Field(..., description="Total expenses for the month")
    net: Decimal = Field(..., description="Net cashflow (income - expenses)")
    currency: str = Field(..., description="Currency code")

    model_config = ConfigDict(from_attributes=True)


class CashflowReport(BaseModel):
    """Monthly cashflow report."""

    start_date: DateType = Field(..., description="Report start date")
    end_date: DateType = Field(..., description="Report end date")
    currency: str = Field(..., description="Primary currency for the report")
    data: List[CashflowDataPoint] = Field(..., description="Monthly cashflow data")
    total_income: Decimal = Field(..., description="Total income for the period")
    total_expenses: Decimal = Field(..., description="Total expenses for the period")
    net_cashflow: Decimal = Field(..., description="Net cashflow for the period")

    model_config = ConfigDict(from_attributes=True)


class CategorySpending(BaseModel):
    """Spending breakdown by category."""

    category_id: Optional[int] = Field(None, description="Category ID (null for uncategorized)")
    category_name: str = Field(..., description="Category name")
    total_amount: Decimal = Field(..., description="Total spent in this category")
    transaction_count: int = Field(..., description="Number of transactions")
    percentage: Decimal = Field(..., description="Percentage of total spending")

    model_config = ConfigDict(from_attributes=True)


class SpendingReport(BaseModel):
    """Spending analysis by category."""

    start_date: DateType = Field(..., description="Report start date")
    end_date: DateType = Field(..., description="Report end date")
    currency: str = Field(..., description="Currency for the report")
    categories: List[CategorySpending] = Field(..., description="Spending by category")
    total_spending: Decimal = Field(..., description="Total spending for the period")
    total_transactions: int = Field(..., description="Total number of transactions")

    model_config = ConfigDict(from_attributes=True)


class IncomeSource(BaseModel):
    """Income breakdown by category."""

    category_id: Optional[int] = Field(None, description="Category ID (null for uncategorized)")
    category_name: str = Field(..., description="Category name")
    total_amount: Decimal = Field(..., description="Total income from this source")
    transaction_count: int = Field(..., description="Number of transactions")
    percentage: Decimal = Field(..., description="Percentage of total income")

    model_config = ConfigDict(from_attributes=True)


class IncomeReport(BaseModel):
    """Income analysis report."""

    start_date: DateType = Field(..., description="Report start date")
    end_date: DateType = Field(..., description="Report end date")
    currency: str = Field(..., description="Currency for the report")
    sources: List[IncomeSource] = Field(..., description="Income by source")
    total_income: Decimal = Field(..., description="Total income for the period")
    total_transactions: int = Field(..., description="Total number of income transactions")
    average_monthly_income: Decimal = Field(..., description="Average monthly income")

    model_config = ConfigDict(from_attributes=True)


class NetWorthDataPoint(BaseModel):
    """Net worth at a specific point in time."""

    date: DateType = Field(..., description="Date of the snapshot")
    total_assets: Decimal = Field(..., description="Total assets (positive balances)")
    total_liabilities: Decimal = Field(..., description="Total liabilities (negative balances)")
    net_worth: Decimal = Field(..., description="Net worth (assets - liabilities)")
    currency: str = Field(..., description="Currency code")

    model_config = ConfigDict(from_attributes=True)


class AccountBalance(BaseModel):
    """Account balance at a specific point in time."""

    account_id: int = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    account_type: str = Field(..., description="Account type")
    balance: Decimal = Field(..., description="Account balance")
    currency: str = Field(..., description="Currency code")

    model_config = ConfigDict(from_attributes=True)


class NetWorthReport(BaseModel):
    """Net worth timeline report."""

    start_date: DateType = Field(..., description="Report start date")
    end_date: DateType = Field(..., description="Report end date")
    currency: str = Field(..., description="Primary currency for the report")
    timeline: List[NetWorthDataPoint] = Field(..., description="Net worth over time")
    current_net_worth: Decimal = Field(..., description="Current net worth")
    change: Decimal = Field(..., description="Change in net worth over the period")
    change_percentage: Decimal = Field(..., description="Percentage change in net worth")
    accounts: List[AccountBalance] = Field(..., description="Current account balances")

    model_config = ConfigDict(from_attributes=True)
