"""
Portfolio Benchmark Model

Link portfolios to benchmarks for comparison.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    Numeric,
    DateTime,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PortfolioBenchmark(Base):
    """Portfolio benchmark model for linking portfolios to benchmarks."""

    __tablename__ = "portfolio_benchmarks"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign Keys
    portfolio_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False
    )
    benchmark_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("benchmarks.id", ondelete="CASCADE"),
        nullable=False
    )

    # Benchmark Weight
    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("100.00"),
        server_default="100.00"
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="benchmarks")
    benchmark: Mapped["Benchmark"] = relationship("Benchmark", back_populates="portfolio_benchmarks")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("portfolio_id", "benchmark_id", name="uq_portfolio_benchmark"),
        CheckConstraint(
            "weight > 0 AND weight <= 100",
            name="chk_weight_range"
        ),
        Index("idx_portfolio_benchmarks_portfolio_id", "portfolio_id"),
        Index("idx_portfolio_benchmarks_benchmark_id", "benchmark_id"),
    )

    def __repr__(self) -> str:
        return f"<PortfolioBenchmark(id={self.id}, portfolio_id={self.portfolio_id}, benchmark_id={self.benchmark_id})>"
