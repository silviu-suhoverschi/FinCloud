from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    Date,
    Numeric,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.budget import Budget

"""
Budget Spending Cache Model

Denormalized table for fast budget progress queries.
"""


class BudgetSpendingCache(Base):
    """Budget spending cache for performance optimization."""

    __tablename__ = "budget_spending_cache"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign Keys
    budget_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("budgets.id", ondelete="CASCADE"),
        nullable=False
    )

    # Period Information
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)

    # Spending Information
    total_spent: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0"
    )
    total_budget: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    # Cache Metadata
    last_calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    budget: Mapped["Budget"] = relationship("Budget", back_populates="spending_cache")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("budget_id", "period_start", name="uq_budget_period"),
        Index("idx_budget_spending_cache_budget_id", "budget_id"),
        Index("idx_budget_spending_cache_period", "period_start", "period_end"),
    )

    def __repr__(self) -> str:
        return f"<BudgetSpendingCache(id={self.id}, budget_id={self.budget_id}, spent={self.total_spent})>"
