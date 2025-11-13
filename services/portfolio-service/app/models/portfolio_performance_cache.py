from __future__ import annotations

from datetime import datetime, date
from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    Date,
    Numeric,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.portfolio import Portfolio

"""
Portfolio Performance Cache Model

Cached performance metrics for fast retrieval.
"""


class PortfolioPerformanceCache(Base):
    """Portfolio performance cache for fast performance retrieval."""

    __tablename__ = "portfolio_performance_cache"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign Keys
    portfolio_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False
    )

    # Performance Date
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # Portfolio Metrics
    total_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_cost_basis: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_gain_loss: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    total_gain_loss_percent: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    daily_return: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))

    # Income and Fees
    dividends_received: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default="0"
    )
    fees_paid: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0"), server_default="0"
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(
        "Portfolio", back_populates="performance_cache"
    )

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("portfolio_id", "date", name="uq_portfolio_date"),
        Index("idx_portfolio_performance_cache_portfolio_id", "portfolio_id"),
        Index(
            "idx_portfolio_performance_cache_date",
            "date",
            postgresql_ops={"date": "DESC"},
        ),
        Index(
            "idx_portfolio_performance_cache_portfolio_date",
            "portfolio_id",
            "date",
            postgresql_ops={"date": "DESC"},
        ),
    )

    def __repr__(self) -> str:
        return f"<PortfolioPerformanceCache(id={self.id}, portfolio_id={self.portfolio_id}, date={self.date})>"
