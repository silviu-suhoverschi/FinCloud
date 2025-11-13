"""
Pydantic schemas for category management.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class CategoryType(str, Enum):
    """Valid category types."""

    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class CategoryBase(BaseModel):
    """Base schema for category."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Category name"
    )
    type: CategoryType = Field(..., description="Category type")
    parent_id: Optional[int] = Field(
        None, description="Parent category ID for hierarchical categories"
    )
    color: Optional[str] = Field(
        None, min_length=7, max_length=7, pattern="^#[0-9A-Fa-f]{6}$",
        description="Category color in hex format (e.g., #FF5733)"
    )
    icon: Optional[str] = Field(
        None, max_length=50, description="Icon identifier"
    )
    is_active: bool = Field(
        default=True, description="Whether the category is active"
    )
    sort_order: int = Field(
        default=0, description="Sort order for displaying categories"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate category name."""
        if not v.strip():
            raise ValueError("Category name cannot be empty or whitespace")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color format."""
        if v:
            return v.upper()
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Category name"
    )
    type: Optional[CategoryType] = Field(None, description="Category type")
    parent_id: Optional[int] = Field(
        None, description="Parent category ID"
    )
    color: Optional[str] = Field(
        None, min_length=7, max_length=7, pattern="^#[0-9A-Fa-f]{6}$",
        description="Category color in hex format"
    )
    icon: Optional[str] = Field(
        None, max_length=50, description="Icon identifier"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the category is active"
    )
    sort_order: Optional[int] = Field(
        None, description="Sort order"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name."""
        if v is not None and not v.strip():
            raise ValueError("Category name cannot be empty or whitespace")
        return v.strip() if v else v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color format."""
        if v:
            return v.upper()
        return v


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    id: int = Field(..., description="Category ID")
    uuid: UUID = Field(..., description="Category UUID")
    user_id: int = Field(..., description="User ID who owns the category")
    created_at: datetime = Field(..., description="Category creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    deleted_at: Optional[datetime] = Field(
        None, description="Deletion timestamp (soft delete)"
    )

    model_config = ConfigDict(from_attributes=True)


class CategoryWithChildren(CategoryResponse):
    """Schema for category with children."""

    children: list["CategoryWithChildren"] = Field(
        default_factory=list, description="Child categories"
    )

    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    """Schema for category list response."""

    total: int = Field(..., description="Total number of categories")
    categories: list[CategoryResponse] = Field(
        ..., description="List of categories"
    )


class CategoryTree(BaseModel):
    """Schema for hierarchical category tree response."""

    categories: list[CategoryWithChildren] = Field(
        ..., description="Tree of categories with their children"
    )
