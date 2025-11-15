"""
Pydantic schemas for API keys.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ApiKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(..., min_length=1, max_length=100, description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    permissions: str = Field(
        default="read", description="Permissions (read, write, admin)"
    )
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class ApiKeyResponse(BaseModel):
    """Schema for API key response (without the actual key)."""

    id: int = Field(..., description="API key ID")
    uuid: UUID = Field(..., description="API key UUID")
    name: str = Field(..., description="API key name")
    description: Optional[str] = Field(None, description="API key description")
    key_prefix: str = Field(..., description="API key prefix for identification")
    permissions: str = Field(..., description="Permissions")
    is_active: bool = Field(..., description="Whether the key is active")
    last_used_at: Optional[datetime] = Field(None, description="Last usage timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ApiKeyWithSecret(ApiKeyResponse):
    """Schema for API key response with the actual secret key (shown only once)."""

    key: str = Field(..., description="The actual API key (shown only once)")


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="API key name"
    )
    description: Optional[str] = Field(None, description="API key description")
    permissions: Optional[str] = Field(None, description="Permissions")
    is_active: Optional[bool] = Field(None, description="Whether the key is active")
