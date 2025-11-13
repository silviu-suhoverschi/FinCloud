"""
Pydantic schemas for transaction management.
"""

from __future__ import annotations

from datetime import datetime
from datetime import date as DateType
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TransactionType(str, Enum):
    """Valid transaction types."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class TransactionBase(BaseModel):
    """Base schema for transaction."""

    account_id: int = Field(..., description="Account ID for the transaction")
    type: TransactionType = Field(..., description="Transaction type")
    amount: Decimal = Field(
        ..., gt=0, description="Transaction amount (must be positive)"
    )
    currency: str = Field(
        ..., min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    date: DateType = Field(..., description="Transaction date")
    description: str = Field(
        ..., min_length=1, max_length=1000, description="Transaction description"
    )
    category_id: Optional[int] = Field(
        None, description="Category ID (optional for transfers)"
    )
    destination_account_id: Optional[int] = Field(
        None, description="Destination account ID (required for transfers)"
    )
    payee: Optional[str] = Field(None, max_length=255, description="Payee name")
    reference_number: Optional[str] = Field(
        None, max_length=100, description="Reference number (e.g., check number)"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: Optional[list[str]] = Field(None, description="Tags for categorization")
    exchange_rate: Decimal = Field(
        default=Decimal("1.0"),
        gt=0,
        description="Exchange rate (default: 1.0)",
    )
    is_reconciled: bool = Field(
        default=False, description="Whether transaction is reconciled"
    )
    external_id: Optional[str] = Field(
        None, max_length=255, description="External ID from import"
    )
    import_source: Optional[str] = Field(
        None, max_length=50, description="Source of import (e.g., 'csv', 'api')"
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if len(v) != 3:
            raise ValueError("Currency code must be exactly 3 characters (ISO 4217)")
        return v.upper()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description."""
        if not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate tags."""
        if v:
            # Remove empty tags and strip whitespace
            cleaned_tags = [tag.strip() for tag in v if tag.strip()]
            return cleaned_tags if cleaned_tags else None
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction."""

    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    account_id: Optional[int] = Field(None, description="Account ID")
    type: Optional[TransactionType] = Field(None, description="Transaction type")
    amount: Optional[Decimal] = Field(None, gt=0, description="Transaction amount")
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code"
    )
    date: Optional[DateType] = Field(None, description="Transaction date")
    description: Optional[str] = Field(
        None, min_length=1, max_length=1000, description="Transaction description"
    )
    category_id: Optional[int] = Field(None, description="Category ID")
    destination_account_id: Optional[int] = Field(
        None, description="Destination account ID"
    )
    payee: Optional[str] = Field(None, max_length=255, description="Payee name")
    reference_number: Optional[str] = Field(
        None, max_length=100, description="Reference number"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    tags: Optional[list[str]] = Field(None, description="Tags")
    exchange_rate: Optional[Decimal] = Field(None, gt=0, description="Exchange rate")
    is_reconciled: Optional[bool] = Field(
        None, description="Whether transaction is reconciled"
    )

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

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description."""
        if v is not None and not v.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        """Validate tags."""
        if v:
            cleaned_tags = [tag.strip() for tag in v if tag.strip()]
            return cleaned_tags if cleaned_tags else None
        return v


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""

    id: int = Field(..., description="Transaction ID")
    uuid: UUID = Field(..., description="Transaction UUID")
    user_id: int = Field(..., description="User ID who owns the transaction")
    reconciled_at: Optional[datetime] = Field(
        None, description="When transaction was reconciled"
    )
    recurring_transaction_id: Optional[int] = Field(
        None, description="ID of recurring transaction template"
    )
    created_at: datetime = Field(..., description="Transaction creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    class Config:
        from_attributes = True


class TransactionList(BaseModel):
    """Schema for paginated transaction list response."""

    total: int = Field(..., description="Total number of transactions")
    transactions: list[TransactionResponse] = Field(
        ..., description="List of transactions"
    )


class TransactionBulkCreate(BaseModel):
    """Schema for bulk transaction creation from CSV."""

    transactions: list[TransactionCreate] = Field(
        ..., description="List of transactions to create"
    )


class TransactionBulkResponse(BaseModel):
    """Schema for bulk transaction creation response."""

    created: int = Field(..., description="Number of transactions created")
    failed: int = Field(..., description="Number of transactions that failed")
    errors: list[dict] = Field(
        default_factory=list, description="List of errors for failed transactions"
    )
    transactions: list[TransactionResponse] = Field(
        default_factory=list, description="List of created transactions"
    )


class TransactionSearchParams(BaseModel):
    """Schema for transaction search parameters."""

    query: str = Field(..., min_length=1, description="Search query")
    account_id: Optional[int] = Field(None, description="Filter by account ID")
    type: Optional[TransactionType] = Field(
        None, description="Filter by transaction type"
    )
    category_id: Optional[int] = Field(None, description="Filter by category ID")
    date_from: Optional[DateType] = Field(None, description="Filter by start date")
    date_to: Optional[DateType] = Field(None, description="Filter by end date")
    min_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum amount")
    max_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum amount")
    tags: Optional[list[str]] = Field(None, description="Filter by tags")
    is_reconciled: Optional[bool] = Field(
        None, description="Filter by reconciled status"
    )
