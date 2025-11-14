"""
Pydantic schemas for holding management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class HoldingBase(BaseModel):
    """Base schema for holding."""

    portfolio_id: int = Field(..., gt=0, description="Portfolio ID")
    asset_id: int = Field(..., gt=0, description="Asset ID")
    quantity: Decimal = Field(..., ge=0, description="Quantity of the asset held")
    average_cost: Decimal = Field(
        default=Decimal("0"), ge=0, description="Average cost per unit"
    )
    notes: Optional[str] = Field(None, description="Additional notes about the holding")

    @field_validator("quantity", "average_cost")
    @classmethod
    def validate_non_negative(cls, v: Decimal) -> Decimal:
        """Validate that quantity and cost are non-negative."""
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v


class HoldingCreate(HoldingBase):
    """Schema for creating a new holding."""

    pass


class HoldingUpdate(BaseModel):
    """Schema for updating a holding."""

    quantity: Optional[Decimal] = Field(
        None, ge=0, description="Quantity of the asset held"
    )
    average_cost: Optional[Decimal] = Field(
        None, ge=0, description="Average cost per unit"
    )
    notes: Optional[str] = Field(None, description="Additional notes about the holding")

    @field_validator("quantity", "average_cost")
    @classmethod
    def validate_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that quantity and cost are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Value must be non-negative")
        return v


class HoldingResponse(BaseModel):
    """Schema for holding response."""

    id: int = Field(..., description="Holding ID")
    uuid: UUID = Field(..., description="Holding UUID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    asset_id: int = Field(..., description="Asset ID")
    quantity: Decimal = Field(..., description="Quantity of the asset held")
    average_cost: Decimal = Field(..., description="Average cost per unit")
    cost_basis: Decimal = Field(
        ..., description="Total cost basis (quantity × average_cost)"
    )
    current_price: Optional[Decimal] = Field(None, description="Current market price")
    current_value: Optional[Decimal] = Field(None, description="Current market value")
    unrealized_gain_loss: Optional[Decimal] = Field(
        None, description="Unrealized gain/loss amount"
    )
    unrealized_gain_loss_percent: Optional[Decimal] = Field(
        None, description="Unrealized gain/loss percentage"
    )
    last_price_update: Optional[datetime] = Field(
        None, description="Last price update timestamp"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    model_config = ConfigDict(from_attributes=True)


class HoldingWithAssetResponse(HoldingResponse):
    """Schema for holding response with asset details."""

    asset_symbol: Optional[str] = Field(None, description="Asset symbol")
    asset_name: Optional[str] = Field(None, description="Asset name")
    asset_type: Optional[str] = Field(None, description="Asset type")
    asset_currency: Optional[str] = Field(None, description="Asset currency")


class HoldingList(BaseModel):
    """Schema for paginated holding list response."""

    total: int = Field(..., description="Total number of holdings")
    holdings: list[HoldingResponse] = Field(..., description="List of holdings")
