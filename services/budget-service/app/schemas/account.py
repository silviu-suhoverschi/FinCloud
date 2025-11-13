"""
Pydantic schemas for account management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
import re


class AccountType:
    """Valid account types."""

    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    CASH = "cash"
    INVESTMENT = "investment"
    LOAN = "loan"
    MORTGAGE = "mortgage"
    OTHER = "other"

    @classmethod
    def values(cls):
        """Get all valid account type values."""
        return [
            cls.CHECKING,
            cls.SAVINGS,
            cls.CREDIT_CARD,
            cls.CASH,
            cls.INVESTMENT,
            cls.LOAN,
            cls.MORTGAGE,
            cls.OTHER,
        ]


class AccountBase(BaseModel):
    """Base schema for account."""

    name: str = Field(..., min_length=1, max_length=255, description="Account name")
    type: str = Field(..., description="Account type")
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)",
    )
    initial_balance: Decimal = Field(
        default=Decimal("0.00"), description="Initial balance"
    )
    account_number: Optional[str] = Field(
        None, max_length=100, description="Account number (optional)"
    )
    institution: Optional[str] = Field(
        None, max_length=255, description="Financial institution name (optional)"
    )
    color: Optional[str] = Field(
        None, max_length=7, description="Color in hex format (#RRGGBB, optional)"
    )
    icon: Optional[str] = Field(None, max_length=50, description="Icon name (optional)")
    is_active: bool = Field(default=True, description="Whether account is active")
    include_in_net_worth: bool = Field(
        default=True, description="Whether to include in net worth calculations"
    )
    notes: Optional[str] = Field(None, description="Additional notes (optional)")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate account type."""
        valid_types = AccountType.values()
        if v not in valid_types:
            raise ValueError(f"Account type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if len(v) != 3:
            raise ValueError("Currency code must be exactly 3 characters (ISO 4217)")
        return v.upper()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color hex format."""
        if v:
            color_pattern = r"^#[0-9A-Fa-f]{6}$"
            if not re.match(color_pattern, v):
                raise ValueError("Color must be in hex format (#RRGGBB)")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate account name."""
        if not v.strip():
            raise ValueError("Account name cannot be empty or whitespace")
        return v.strip()


class AccountCreate(AccountBase):
    """Schema for creating a new account."""

    pass


class AccountUpdate(BaseModel):
    """Schema for updating an account."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Account name"
    )
    type: Optional[str] = Field(None, description="Account type")
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    account_number: Optional[str] = Field(
        None, max_length=100, description="Account number"
    )
    institution: Optional[str] = Field(
        None, max_length=255, description="Institution name"
    )
    color: Optional[str] = Field(None, max_length=7, description="Color in hex format")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name")
    is_active: Optional[bool] = Field(None, description="Whether account is active")
    include_in_net_worth: Optional[bool] = Field(
        None, description="Whether to include in net worth"
    )
    notes: Optional[str] = Field(None, description="Additional notes")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate account type."""
        if v:
            valid_types = AccountType.values()
            if v not in valid_types:
                raise ValueError(
                    f"Account type must be one of: {', '.join(valid_types)}"
                )
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code."""
        if v:
            if len(v) != 3:
                raise ValueError(
                    "Currency code must be exactly 3 characters (ISO 4217)"
                )
            return v.upper()
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color hex format."""
        if v:
            color_pattern = r"^#[0-9A-Fa-f]{6}$"
            if not re.match(color_pattern, v):
                raise ValueError("Color must be in hex format (#RRGGBB)")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate account name."""
        if v is not None and not v.strip():
            raise ValueError("Account name cannot be empty or whitespace")
        return v.strip() if v else v


class AccountResponse(AccountBase):
    """Schema for account response."""

    id: int = Field(..., description="Account ID")
    uuid: UUID = Field(..., description="Account UUID")
    user_id: int = Field(..., description="User ID who owns the account")
    current_balance: Decimal = Field(..., description="Current account balance")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    class Config:
        from_attributes = True


class AccountBalance(BaseModel):
    """Schema for account balance response."""

    account_id: int = Field(..., description="Account ID")
    uuid: UUID = Field(..., description="Account UUID")
    name: str = Field(..., description="Account name")
    currency: str = Field(..., description="Currency code")
    current_balance: Decimal = Field(..., description="Current balance")
    initial_balance: Decimal = Field(..., description="Initial balance")
    balance_change: Decimal = Field(..., description="Change from initial balance")
    last_updated: datetime = Field(..., description="Last balance update timestamp")

    class Config:
        from_attributes = True


class AccountList(BaseModel):
    """Schema for paginated account list response."""

    total: int = Field(..., description="Total number of accounts")
    accounts: list[AccountResponse] = Field(..., description="List of accounts")
