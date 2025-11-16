"""
Pydantic schemas for budget management.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class CategoryInfo(BaseModel):
    """Simplified category information for budget responses."""

    id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    type: str = Field(..., description="Category type")

    model_config = ConfigDict(from_attributes=True)


class BudgetPeriod(str, Enum):
    """Valid budget periods."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class BudgetBase(BaseModel):
    """Base schema for budget."""

    name: str = Field(..., min_length=1, max_length=255, description="Budget name")
    amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=15,
        decimal_places=2,
        description="Budget amount (must be positive)",
    )
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)",
    )
    period: BudgetPeriod = Field(..., description="Budget period")
    start_date: date = Field(..., description="Budget start date")
    end_date: Optional[date] = Field(None, description="Budget end date (optional)")
    category_id: Optional[int] = Field(
        None, description="Category ID (required if account_id is not provided)"
    )
    account_id: Optional[int] = Field(
        None, description="Account ID (required if category_id is not provided)"
    )
    rollover_unused: bool = Field(
        default=False, description="Whether to rollover unused budget to next period"
    )
    alert_enabled: bool = Field(
        default=True, description="Whether to enable budget alerts"
    )
    alert_threshold: Decimal = Field(
        default=Decimal("80.00"),
        ge=0,
        le=100,
        description="Alert threshold percentage (0-100)",
    )
    is_active: bool = Field(default=True, description="Whether budget is active")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate budget name."""
        if not v.strip():
            raise ValueError("Budget name cannot be empty or whitespace")
        return v.strip()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        return v.upper()

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        """Validate end date is after start date."""
        if v is not None and "start_date" in info.data:
            start_date = info.data["start_date"]
            if v < start_date:
                raise ValueError("End date must be after start date")
        return v

    def model_post_init(self, __context) -> None:
        """Validate that at least one of category_id or account_id is provided."""
        if self.category_id is None and self.account_id is None:
            raise ValueError("Either category_id or account_id must be provided")


class BudgetCreate(BudgetBase):
    """Schema for creating a new budget."""

    pass


class BudgetUpdate(BaseModel):
    """Schema for updating a budget."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Budget name"
    )
    amount: Optional[Decimal] = Field(
        None,
        gt=0,
        max_digits=15,
        decimal_places=2,
        description="Budget amount (must be positive)",
    )
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code"
    )
    period: Optional[BudgetPeriod] = Field(None, description="Budget period")
    start_date: Optional[date] = Field(None, description="Budget start date")
    end_date: Optional[date] = Field(None, description="Budget end date")
    category_id: Optional[int] = Field(None, description="Category ID")
    account_id: Optional[int] = Field(None, description="Account ID")
    rollover_unused: Optional[bool] = Field(
        None, description="Whether to rollover unused budget"
    )
    alert_enabled: Optional[bool] = Field(None, description="Enable budget alerts")
    alert_threshold: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Alert threshold percentage"
    )
    is_active: Optional[bool] = Field(None, description="Whether budget is active")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate budget name."""
        if v is not None and not v.strip():
            raise ValueError("Budget name cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code."""
        return v.upper() if v else v


class BudgetResponse(BudgetBase):
    """Schema for budget response."""

    id: int = Field(..., description="Budget ID")
    uuid: UUID = Field(..., description="Budget UUID")
    user_id: int = Field(..., description="User ID who owns the budget")
    category: Optional[CategoryInfo] = Field(
        None, description="Category information if budget is for a category"
    )
    created_at: datetime = Field(..., description="Budget creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    model_config = ConfigDict(from_attributes=True)


class BudgetWithSpending(BudgetResponse):
    """Schema for budget with spending information."""

    total_spent: Decimal = Field(
        default=Decimal("0.00"), description="Total amount spent"
    )
    remaining: Decimal = Field(default=Decimal("0.00"), description="Remaining amount")
    percentage_used: Decimal = Field(
        default=Decimal("0.00"), description="Percentage of budget used"
    )
    transaction_count: int = Field(default=0, description="Number of transactions")
    is_over_budget: bool = Field(default=False, description="Whether over budget")
    days_remaining: Optional[int] = Field(None, description="Days remaining in period")

    model_config = ConfigDict(from_attributes=True)


class BudgetProgress(BaseModel):
    """Schema for budget progress tracking."""

    budget_id: int = Field(..., description="Budget ID")
    budget_name: str = Field(..., description="Budget name")
    amount: Decimal = Field(..., description="Budget amount")
    currency: str = Field(..., description="Currency code")
    period: str = Field(..., description="Budget period")
    start_date: date = Field(..., description="Period start date")
    end_date: Optional[date] = Field(None, description="Period end date")
    total_spent: Decimal = Field(..., description="Total amount spent")
    remaining: Decimal = Field(..., description="Remaining amount")
    percentage_used: Decimal = Field(..., description="Percentage of budget used")
    transaction_count: int = Field(..., description="Number of transactions")
    is_over_budget: bool = Field(..., description="Whether over budget")
    days_remaining: Optional[int] = Field(None, description="Days remaining in period")
    alert_threshold: Decimal = Field(..., description="Alert threshold percentage")
    should_alert: bool = Field(..., description="Whether an alert should be triggered")


class BudgetList(BaseModel):
    """Schema for budget list response."""

    total: int = Field(..., description="Total number of budgets")
    budgets: list[BudgetResponse] = Field(..., description="List of budgets")
