from __future__ import annotations

"""
Portfolio Transaction Model

Buy, sell, dividend, and other portfolio transactions.
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Date,
    Numeric,
    DateTime,
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


class PortfolioTransaction(Base):
    """Portfolio transaction model for buy, sell, dividend, and other transactions."""

    __tablename__ = "portfolio_transactions"

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

    # Transaction Details
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Fees and Taxes
    fee: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0"
    )
    tax: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0"),
        server_default="0"
    )

    # Currency and Exchange Rate
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(15, 6),
        default=Decimal("1.0"),
        server_default="1.0"
    )

    # Transaction Info
    date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    reference_number: Mapped[str | None] = mapped_column(String(100))

    # Import Information
    external_id: Mapped[str | None] = mapped_column(String(255))
    import_source: Mapped[str | None] = mapped_column(String(50))

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
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="transactions")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="transactions")

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('buy', 'sell', 'dividend', 'interest', 'fee', 'tax', 'split', 'transfer_in', 'transfer_out')",
            name="chk_portfolio_transaction_type"
        ),
        CheckConstraint(
            "quantity > 0 OR type IN ('fee', 'tax')",
            name="chk_quantity_positive"
        ),
        CheckConstraint(
            "price >= 0",
            name="chk_price_non_negative"
        ),
        CheckConstraint(
            "fee >= 0",
            name="chk_fee_non_negative"
        ),
        CheckConstraint(
            "tax >= 0",
            name="chk_tax_non_negative"
        ),
        Index("idx_portfolio_transactions_portfolio_id", "portfolio_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_portfolio_transactions_asset_id", "asset_id"),
        Index("idx_portfolio_transactions_type", "type"),
        Index("idx_portfolio_transactions_date", "date", postgresql_ops={"date": "DESC"}),
        Index("idx_portfolio_transactions_created_at", "created_at", postgresql_ops={"created_at": "DESC"}),
        # Composite indexes for common query patterns
        Index("idx_portfolio_transactions_portfolio_date", "portfolio_id", "date", postgresql_ops={"date": "DESC"}, postgresql_where="deleted_at IS NULL"),
        Index("idx_portfolio_transactions_asset_date", "asset_id", "date", postgresql_ops={"date": "DESC"}, postgresql_where="deleted_at IS NULL"),
        Index("idx_portfolio_transactions_portfolio_type", "portfolio_id", "type", "date", postgresql_ops={"date": "DESC"}, postgresql_where="deleted_at IS NULL"),
    )

    def __repr__(self) -> str:
        return f"<PortfolioTransaction(id={self.id}, type='{self.type}', quantity={self.quantity}, price={self.price})>"
