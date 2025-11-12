from __future__ import annotations

"""
Budget Model

Budget allocations for categories or accounts.
"""

from datetime import datetime, date
from typing import List
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Budget(Base):
    """Budget model for budget allocations."""

    __tablename__ = "budgets"

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
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE")
    )
    account_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("accounts.id", ondelete="CASCADE")
    )

    # Budget Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Period Information
    period: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)

    # Budget Settings
    rollover_unused: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    alert_threshold: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("80.00"),
        server_default="80.00"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

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
    user: Mapped["User"] = relationship("User", back_populates="budgets")
    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="budgets"
    )
    account: Mapped["Account | None"] = relationship(
        "Account",
        back_populates="budgets"
    )
    spending_cache: Mapped[List["BudgetSpendingCache"]] = relationship(
        "BudgetSpendingCache",
        back_populates="budget",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            "category_id IS NOT NULL OR account_id IS NOT NULL",
            name="chk_budget_has_category_or_account"
        ),
        CheckConstraint(
            "period IN ('daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom')",
            name="chk_budget_period"
        ),
        CheckConstraint(
            "amount > 0",
            name="chk_amount_positive"
        ),
        CheckConstraint(
            "alert_threshold >= 0 AND alert_threshold <= 100",
            name="chk_alert_threshold_range"
        ),
        CheckConstraint(
            "end_date IS NULL OR end_date >= start_date",
            name="chk_end_date_after_start"
        ),
        Index("idx_budgets_user_id", "user_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_budgets_category_id", "category_id"),
        Index("idx_budgets_account_id", "account_id"),
        Index("idx_budgets_period", "period"),
        Index("idx_budgets_start_date", "start_date"),
        Index("idx_budgets_is_active", "is_active"),
        # Composite indexes for common query patterns
        Index("idx_budgets_user_active_period", "user_id", "is_active", "period", postgresql_where="deleted_at IS NULL"),
        Index("idx_budgets_user_start_date", "user_id", "start_date", postgresql_ops={"start_date": "DESC"}, postgresql_where="deleted_at IS NULL"),
    )

    def __repr__(self) -> str:
        return f"<Budget(id={self.id}, name='{self.name}', amount={self.amount})>"
