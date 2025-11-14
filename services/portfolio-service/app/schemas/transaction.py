"""
Pydantic schemas for portfolio transaction management.
"""

from __future__ import annotations

from datetime import datetime
from datetime import date as DateType
from typing import Optional
from uuid import UUID
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TransactionType(str, Enum):
    """Transaction types supported by the system."""

    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    INTEREST = "interest"
    FEE = "fee"
    TAX = "tax"
    SPLIT = "split"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class TransactionBase(BaseModel):
    """Base schema for portfolio transaction."""

    portfolio_id: int = Field(..., gt=0, description="Portfolio ID")
    asset_id: int = Field(..., gt=0, description="Asset ID")
    type: TransactionType = Field(..., description="Transaction type")
    quantity: Decimal = Field(..., description="Quantity of the asset")
    price: Decimal = Field(..., ge=0, description="Price per unit")
    total_amount: Decimal = Field(..., description="Total transaction amount")
    fee: Decimal = Field(default=Decimal("0"), ge=0, description="Transaction fee")
    tax: Decimal = Field(default=Decimal("0"), ge=0, description="Transaction tax")
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)",
    )
    exchange_rate: Decimal = Field(
        default=Decimal("1.0"), gt=0, description="Exchange rate to base currency"
    )
    date: DateType = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, description="Additional notes")
    reference_number: Optional[str] = Field(
        None, max_length=100, description="Reference/confirmation number"
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate and uppercase currency code."""
        return v.upper()


class TransactionCreate(TransactionBase):
    """Schema for creating a new portfolio transaction."""

    pass


class TransactionUpdate(BaseModel):
    """Schema for updating a portfolio transaction."""

    type: Optional[TransactionType] = Field(None, description="Transaction type")
    quantity: Optional[Decimal] = Field(None, description="Quantity of the asset")
    price: Optional[Decimal] = Field(None, ge=0, description="Price per unit")
    total_amount: Optional[Decimal] = Field(
        None, description="Total transaction amount"
    )
    fee: Optional[Decimal] = Field(None, ge=0, description="Transaction fee")
    tax: Optional[Decimal] = Field(None, ge=0, description="Transaction tax")
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    exchange_rate: Optional[Decimal] = Field(
        None, gt=0, description="Exchange rate to base currency"
    )
    date: Optional[DateType] = Field(None, description="Transaction date")
    notes: Optional[str] = Field(None, description="Additional notes")
    reference_number: Optional[str] = Field(
        None, max_length=100, description="Reference/confirmation number"
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        """Validate and uppercase currency code."""
        return v.upper() if v is not None else v


class TransactionResponse(BaseModel):
    """Schema for portfolio transaction response."""

    id: int = Field(..., description="Transaction ID")
    uuid: UUID = Field(..., description="Transaction UUID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    asset_id: int = Field(..., description="Asset ID")
    type: str = Field(..., description="Transaction type")
    quantity: Decimal = Field(..., description="Quantity of the asset")
    price: Decimal = Field(..., description="Price per unit")
    total_amount: Decimal = Field(..., description="Total transaction amount")
    fee: Decimal = Field(..., description="Transaction fee")
    tax: Decimal = Field(..., description="Transaction tax")
    currency: str = Field(..., description="Currency code")
    exchange_rate: Decimal = Field(..., description="Exchange rate to base currency")
    date: DateType = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, description="Additional notes")
    reference_number: Optional[str] = Field(
        None, description="Reference/confirmation number"
    )
    external_id: Optional[str] = Field(None, description="External system ID")
    import_source: Optional[str] = Field(None, description="Import source")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    model_config = ConfigDict(from_attributes=True)


class TransactionWithAssetResponse(TransactionResponse):
    """Schema for transaction response with asset details."""

    asset_symbol: Optional[str] = Field(None, description="Asset symbol")
    asset_name: Optional[str] = Field(None, description="Asset name")
    asset_type: Optional[str] = Field(None, description="Asset type")


class TransactionList(BaseModel):
    """Schema for paginated transaction list response."""

    total: int = Field(..., description="Total number of transactions")
    transactions: list[TransactionResponse] = Field(
        ..., description="List of transactions"
    )
