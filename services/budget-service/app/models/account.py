"""
Account Model

Financial accounts (bank, credit card, cash, investment, etc.).
"""

from datetime import datetime
from typing import List
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Numeric,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Account(Base):
    """Account model for financial accounts."""

    __tablename__ = "accounts"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Unique Identifier
    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid()
    )

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Account Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Balance Information
    initial_balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0
    )
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0
    )

    # Account Metadata
    account_number: Mapped[str | None] = mapped_column(String(100))
    institution: Mapped[str | None] = mapped_column(String(255))
    color: Mapped[str | None] = mapped_column(String(7))
    icon: Mapped[str | None] = mapped_column(String(50))

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    include_in_net_worth: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true"
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="account",
        foreign_keys="Transaction.account_id",
        cascade="all, delete-orphan"
    )
    destination_transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="destination_account",
        foreign_keys="Transaction.destination_account_id",
        cascade="all, delete-orphan"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget",
        back_populates="account",
        cascade="all, delete-orphan"
    )
    recurring_transactions: Mapped[List["RecurringTransaction"]] = relationship(
        "RecurringTransaction",
        back_populates="account",
        foreign_keys="RecurringTransaction.account_id",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('checking', 'savings', 'credit_card', 'cash', 'investment', 'loan', 'mortgage', 'other')",
            name="chk_account_type"
        ),
        CheckConstraint(
            "LENGTH(currency) = 3",
            name="chk_currency_length"
        ),
        CheckConstraint(
            "color IS NULL OR color ~* '^#[0-9A-Fa-f]{6}$'",
            name="chk_color_format"
        ),
        CheckConstraint(
            "current_balance > -999999999999.99 AND current_balance < 999999999999.99",
            name="chk_balance_precision"
        ),
        Index("idx_accounts_user_id", "user_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_accounts_type", "type"),
        Index("idx_accounts_is_active", "is_active"),
        Index("idx_accounts_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name='{self.name}', type='{self.type}')>"
