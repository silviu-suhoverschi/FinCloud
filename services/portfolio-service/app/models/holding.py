"""
Holding Model

Current holdings in portfolios.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    Numeric,
    DateTime,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Holding(Base):
    """Holding model for portfolio holdings."""

    __tablename__ = "holdings"

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
    portfolio_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False
    )
    asset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False
    )

    # Holding Information
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 8),
        nullable=False,
        default=Decimal("0")
    )
    average_cost: Mapped[Decimal] = mapped_column(
        Numeric(15, 4),
        nullable=False,
        default=Decimal("0")
    )
    cost_basis: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=Decimal("0")
    )

    # Current Market Data
    current_price: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    current_value: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))

    # Performance Metrics
    unrealized_gain_loss: Mapped[Decimal | None] = mapped_column(Numeric(15, 2))
    unrealized_gain_loss_percent: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    last_price_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

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
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="holdings")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="holdings")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("portfolio_id", "asset_id", name="uq_portfolio_asset"),
        CheckConstraint(
            "average_cost >= 0",
            name="chk_average_cost_non_negative"
        ),
        CheckConstraint(
            "cost_basis >= 0",
            name="chk_cost_basis_non_negative"
        ),
        Index("idx_holdings_portfolio_id", "portfolio_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_holdings_asset_id", "asset_id"),
        Index("idx_holdings_quantity", "quantity", postgresql_where="quantity > 0"),
    )

    def __repr__(self) -> str:
        return f"<Holding(id={self.id}, portfolio_id={self.portfolio_id}, asset_id={self.asset_id}, quantity={self.quantity})>"
