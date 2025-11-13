from __future__ import annotations

"""
Asset Model

Investment assets (stocks, ETFs, crypto, bonds, etc.).
"""

from datetime import datetime
from typing import List
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Text,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func
import uuid
import re

from app.core.database import Base


class Asset(Base):
    """Asset model for investment assets."""

    __tablename__ = "assets"

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

    # Asset Identifiers
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Asset Type and Classification
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_class: Mapped[str | None] = mapped_column(String(50))
    sector: Mapped[str | None] = mapped_column(String(100))
    exchange: Mapped[str | None] = mapped_column(String(100))

    # Currency and Location
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    country: Mapped[str | None] = mapped_column(String(3))

    # Standard Identifiers
    isin: Mapped[str | None] = mapped_column(String(12))
    cusip: Mapped[str | None] = mapped_column(String(9))
    figi: Mapped[str | None] = mapped_column(String(12))

    # Visual and Metadata
    logo_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    metadata: Mapped[dict | None] = mapped_column(JSONB)

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
        back_populates="asset",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[List["PortfolioTransaction"]] = relationship(
        "PortfolioTransaction",
        back_populates="asset",
        cascade="all, delete-orphan"
    )
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="asset",
        cascade="all, delete-orphan"
    )

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("symbol", "exchange", name="uq_asset_symbol_exchange"),
        CheckConstraint(
            "type IN ('stock', 'etf', 'mutual_fund', 'crypto', 'bond', 'commodity', 'index', 'other')",
            name="chk_asset_type"
        ),
        CheckConstraint(
            "asset_class IS NULL OR asset_class IN ('equity', 'fixed_income', 'real_estate', 'commodity', 'cash', 'alternative', 'cryptocurrency')",
            name="chk_asset_class"
        ),
        CheckConstraint(
            "isin IS NULL OR isin ~* '^[A-Z]{2}[A-Z0-9]{9}[0-9]$'",
            name="chk_isin_format"
        ),
        CheckConstraint(
            "country IS NULL OR LENGTH(country) = 3",
            name="chk_country_code"
        ),
        Index("idx_assets_symbol", "symbol", postgresql_where="deleted_at IS NULL"),
        Index("idx_assets_type", "type"),
        Index("idx_assets_asset_class", "asset_class"),
        Index("idx_assets_sector", "sector"),
        Index("idx_assets_isin", "isin", postgresql_where="isin IS NOT NULL"),
        Index("idx_assets_metadata", "metadata", postgresql_using="gin"),
    )

    # Validators
    @validates("symbol")
    def validate_symbol(self, key, symbol):
        """Validate and normalize symbol."""
        if symbol:
            symbol = symbol.upper().strip()
            if not symbol:
                raise ValueError("Symbol cannot be empty")
        return symbol

    @validates("type")
    def validate_type(self, key, asset_type):
        """Validate asset type."""
        valid_types = ['stock', 'etf', 'mutual_fund', 'crypto', 'bond', 'commodity', 'index', 'other']
        if asset_type and asset_type not in valid_types:
            raise ValueError(f"Asset type must be one of: {', '.join(valid_types)}")
        return asset_type

    @validates("asset_class")
    def validate_asset_class(self, key, asset_class):
        """Validate asset class."""
        valid_classes = ['equity', 'fixed_income', 'real_estate', 'commodity', 'cash', 'alternative', 'cryptocurrency']
        if asset_class and asset_class not in valid_classes:
            raise ValueError(f"Asset class must be one of: {', '.join(valid_classes)}")
        return asset_class

    @validates("currency", "country")
    def validate_iso_code(self, key, code):
        """Validate ISO codes."""
        if code and len(code) != 3:
            raise ValueError(f"{key} code must be exactly 3 characters")
        return code.upper() if code else code

    @validates("isin")
    def validate_isin(self, key, isin):
        """Validate ISIN format."""
        if isin:
            isin = isin.upper().strip()
            isin_pattern = r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$'
            if not re.match(isin_pattern, isin):
                raise ValueError(f"Invalid ISIN format: {isin}")
        return isin

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, symbol='{self.symbol}', name='{self.name}')>"
