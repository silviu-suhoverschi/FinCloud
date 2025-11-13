from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.portfolio_benchmark import PortfolioBenchmark

"""
Benchmark Model

Market benchmarks for comparison (S&P 500, etc.).
"""


class Benchmark(Base):
    """Benchmark model for market benchmarks."""

    __tablename__ = "benchmarks"

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

    # Benchmark Details
    symbol: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    # Asset Reference (optional)
    asset_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("assets.id"))

    # Settings
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
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

    # Relationships
    portfolio_benchmarks: Mapped[List["PortfolioBenchmark"]] = relationship(
        "PortfolioBenchmark", back_populates="benchmark", cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        Index("idx_benchmarks_symbol", "symbol"),
        Index("idx_benchmarks_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Benchmark(id={self.id}, symbol='{self.symbol}', name='{self.name}')>"
