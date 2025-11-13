"""
Pydantic schemas for portfolio management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict


class PortfolioBase(BaseModel):
    """Base schema for portfolio."""

    name: str = Field(..., min_length=1, max_length=255, description="Portfolio name")
    description: Optional[str] = Field(None, description="Portfolio description")
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)",
    )
    is_active: bool = Field(default=True, description="Whether portfolio is active")
    sort_order: int = Field(default=0, description="Sort order for display")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if len(v) != 3:
            raise ValueError("Currency code must be exactly 3 characters (ISO 4217)")
        return v.upper()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate portfolio name."""
        if not v.strip():
            raise ValueError("Portfolio name cannot be empty or whitespace")
        return v.strip()


class PortfolioCreate(PortfolioBase):
    """Schema for creating a new portfolio."""

    pass


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Portfolio name"
    )
    description: Optional[str] = Field(None, description="Portfolio description")
    currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Currency code (ISO 4217)"
    )
    is_active: Optional[bool] = Field(None, description="Whether portfolio is active")
    sort_order: Optional[int] = Field(None, description="Sort order for display")

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

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate portfolio name."""
        if v is not None and not v.strip():
            raise ValueError("Portfolio name cannot be empty or whitespace")
        return v.strip() if v else v


class PortfolioResponse(PortfolioBase):
    """Schema for portfolio response."""

    id: int = Field(..., description="Portfolio ID")
    uuid: UUID = Field(..., description="Portfolio UUID")
    user_id: int = Field(..., description="User ID who owns the portfolio")
    created_at: datetime = Field(..., description="Portfolio creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    model_config = ConfigDict(from_attributes=True)


class PortfolioList(BaseModel):
    """Schema for paginated portfolio list response."""

    total: int = Field(..., description="Total number of portfolios")
    portfolios: list[PortfolioResponse] = Field(..., description="List of portfolios")
