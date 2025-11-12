from __future__ import annotations

"""
Portfolio Model

Investment portfolios owned by users.
"""

from datetime import datetime
from typing import List
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Integer,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Portfolio(Base):
    """Portfolio model for investment portfolios."""

    __tablename__ = "portfolios"

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

    # User Reference (no FK constraint across services)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Portfolio Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    # Settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

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
    holdings: Mapped[List["Holding"]] = relationship(
        "Holding",
        back_populates="portfolio",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[List["PortfolioTransaction"]] = relationship(
        "PortfolioTransaction",
        back_populates="portfolio",
        cascade="all, delete-orphan"
    )
    performance_cache: Mapped[List["PortfolioPerformanceCache"]] = relationship(
        "PortfolioPerformanceCache",
        back_populates="portfolio",
        cascade="all, delete-orphan"
    )
    benchmarks: Mapped[List["PortfolioBenchmark"]] = relationship(
        "PortfolioBenchmark",
        back_populates="portfolio",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_portfolio_name"),
        Index("idx_portfolios_user_id", "user_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_portfolios_is_active", "is_active"),
        Index("idx_portfolios_sort_order", "sort_order"),
    )

    def __repr__(self) -> str:
        return f"<Portfolio(id={self.id}, name='{self.name}')>"
