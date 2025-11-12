"""
Price History Model

Historical price data for assets.
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Date,
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


class PriceHistory(Base):
    """Price history model for asset price tracking."""

    __tablename__ = "price_history"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign Keys
    asset_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False
    )

    # Price Date
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # OHLC Data
    open: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    high: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    low: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))
    close: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(15, 4))

    # Volume
    volume: Mapped[int | None] = mapped_column(BigInteger)

    # Data Source
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    # Relationships
    asset: Mapped["Asset"] = relationship("Asset", back_populates="price_history")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("asset_id", "date", "source", name="uq_asset_date_source"),
        CheckConstraint(
            "open > 0 OR open IS NULL",
            name="chk_ohlc_positive"
        ),
        CheckConstraint(
            "close > 0",
            name="chk_close_positive"
        ),
        CheckConstraint(
            "source IN ('yahoo_finance', 'alpha_vantage', 'coingecko', 'manual', 'import')",
            name="chk_price_source"
        ),
        Index("idx_price_history_asset_id", "asset_id"),
        Index("idx_price_history_date", "date", postgresql_ops={"date": "DESC"}),
        Index("idx_price_history_asset_date", "asset_id", "date", postgresql_ops={"date": "DESC"}),
        Index("idx_price_history_source", "source"),
    )

    def __repr__(self) -> str:
        return f"<PriceHistory(id={self.id}, asset_id={self.asset_id}, date={self.date}, close={self.close})>"
