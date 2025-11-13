from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Integer,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account
    from app.models.category import Category

"""
Recurring Transaction Model

Templates for recurring transactions (subscriptions, salaries, etc.).
"""


class RecurringTransaction(Base):
    """Recurring transaction model for automated transaction templates."""

    __tablename__ = "recurring_transactions"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Unique Identifier
    uuid: Mapped[uuid.UUID] = mapped_column(
        PostgreSQL_UUID(as_uuid=True),
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
    account_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False
    )
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL")
    )
    destination_account_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE")
    )

    # Transaction Details
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payee: Mapped[str | None] = mapped_column(String(255))

    # Recurrence Settings
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)
    interval_count: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    next_occurrence: Mapped[date] = mapped_column(Date, nullable=False)

    # Tracking
    last_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    occurrences_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    max_occurrences: Mapped[int | None] = mapped_column(Integer)

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    auto_create: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

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
    user: Mapped["User"] = relationship("User", back_populates="recurring_transactions")
    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="recurring_transactions",
        foreign_keys=[account_id]
    )
    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="recurring_transactions"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')",
            name="chk_recurring_type"
        ),
        CheckConstraint(
            "frequency IN ('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'yearly')",
            name="chk_recurring_frequency"
        ),
        CheckConstraint(
            "interval_count > 0",
            name="chk_interval_positive"
        ),
        CheckConstraint(
            "amount > 0",
            name="chk_recurring_amount_positive"
        ),
        Index("idx_recurring_transactions_user_id", "user_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_recurring_transactions_account_id", "account_id"),
        Index(
            "idx_recurring_transactions_next_occurrence",
            "next_occurrence",
            postgresql_where="is_active = TRUE AND deleted_at IS NULL"
        ),
        Index("idx_recurring_transactions_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<RecurringTransaction(id={self.id}, description='{self.description}', frequency='{self.frequency}')>"
