from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func
import uuid
import re

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.category import Category
    from app.models.transaction import Transaction
    from app.models.budget import Budget
    from app.models.recurring_transaction import RecurringTransaction
    from app.models.tag import Tag

"""
User Model

Stores user account information and authentication data.
"""


class User(Base):
    """User model for authentication and account management."""

    __tablename__ = "users"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Unique Identifier
    uuid: Mapped[uuid.UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile Information
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))

    # Account Status
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Role-Based Access Control
    role: Mapped[str] = mapped_column(
        String(20), default="user", server_default="user", nullable=False
    )

    # Preferences
    preferred_currency: Mapped[str] = mapped_column(
        String(3), default="USD", server_default="USD"
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="UTC", server_default="UTC"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    accounts: Mapped[List["Account"]] = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    categories: Mapped[List["Category"]] = relationship(
        "Category", back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="user", cascade="all, delete-orphan"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget", back_populates="user", cascade="all, delete-orphan"
    )
    recurring_transactions: Mapped[List["RecurringTransaction"]] = relationship(
        "RecurringTransaction", back_populates="user", cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship(
        "Tag", back_populates="user", cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name="chk_email_format",
        ),
        CheckConstraint(
            "LENGTH(preferred_currency) = 3", name="chk_preferred_currency_length"
        ),
        CheckConstraint("role IN ('user', 'admin', 'premium')", name="chk_role_valid"),
        Index("idx_users_email", "email", postgresql_where="deleted_at IS NULL"),
        Index("idx_users_uuid", "uuid"),
        Index(
            "idx_users_is_active", "is_active", postgresql_where="deleted_at IS NULL"
        ),
        Index("idx_users_role", "role"),
    )

    # Validators
    @validates("email")
    def validate_email(self, key, email):
        """Validate email format."""
        if not email:
            raise ValueError("Email cannot be empty")
        email = email.lower().strip()
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_pattern, email):
            raise ValueError(f"Invalid email format: {email}")
        return email

    @validates("timezone")
    def validate_timezone(self, key, value):
        """Validate that timezone is not empty."""
        if value and not value.strip():
            raise ValueError(f"{key} cannot be empty or whitespace")
        return value.strip() if value else value

    @validates("preferred_currency")
    def validate_currency(self, key, currency):
        """Validate currency code format."""
        if currency:
            currency = currency.strip()
            if not currency:
                raise ValueError("Currency cannot be empty or whitespace")
            if len(currency) != 3:
                raise ValueError("Currency code must be exactly 3 characters")
            return currency.upper()
        return currency

    @validates("role")
    def validate_role(self, key, role):
        """Validate user role."""
        valid_roles = ["user", "admin", "premium"]
        if role not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return role

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
