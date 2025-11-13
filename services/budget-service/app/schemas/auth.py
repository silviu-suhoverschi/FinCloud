"""
Pydantic schemas for authentication and authorization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=100, description="User password (min 8 chars)"
    )
    first_name: Optional[str] = Field(
        None, max_length=100, description="User's first name"
    )
    last_name: Optional[str] = Field(
        None, max_length=100, description="User's last name"
    )
    preferred_currency: str = Field(
        "USD", min_length=3, max_length=3, description="Preferred currency code"
    )
    timezone: str = Field("UTC", max_length=50, description="User's timezone")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

    @field_validator("preferred_currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        return v.upper()


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class Token(BaseModel):
    """Schema for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str = Field(..., description="JWT refresh token")


class AccessToken(BaseModel):
    """Schema for access token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int = Field(..., description="User ID")
    uuid: UUID = Field(..., description="User UUID")
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    is_active: bool = Field(..., description="Whether user account is active")
    is_verified: bool = Field(..., description="Whether user email is verified")
    email_verified_at: Optional[datetime] = Field(
        None, description="Email verification timestamp"
    )
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    preferred_currency: str = Field(..., description="Preferred currency code")
    timezone: str = Field(..., description="User's timezone")
    role: str = Field(..., description="User role")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for user profile update."""

    first_name: Optional[str] = Field(
        None, max_length=100, description="User's first name"
    )
    last_name: Optional[str] = Field(
        None, max_length=100, description="User's last name"
    )
    preferred_currency: Optional[str] = Field(
        None, min_length=3, max_length=3, description="Preferred currency code"
    )
    timezone: Optional[str] = Field(None, max_length=50, description="User's timezone")

    @field_validator("preferred_currency")
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        """Validate currency code."""
        return v.upper() if v else v


class PasswordChange(BaseModel):
    """Schema for password change."""

    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password (min 8 chars)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr = Field(..., description="User email address")


class PasswordReset(BaseModel):
    """Schema for password reset confirmation."""

    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ..., min_length=8, max_length=100, description="New password (min 8 chars)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class RoleEnum(str):
    """User role enumeration."""

    USER = "user"
    ADMIN = "admin"
    PREMIUM = "premium"


class UserWithRole(UserResponse):
    """Schema for user response with role information."""

    role: str = Field(default="user", description="User role")


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request."""

    token: str = Field(..., description="Email verification token")
