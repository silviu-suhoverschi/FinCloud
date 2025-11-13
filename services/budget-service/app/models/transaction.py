from __future__ import annotations

from datetime import datetime, date
from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Date,
    Numeric,
    Text,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account
    from app.models.category import Category

"""
Transaction Model

Financial transactions (income, expenses, transfers).
"""


class Transaction(Base):
    """Transaction model for financial transactions."""

    __tablename__ = "transactions"

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

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("categories.id", ondelete="SET NULL")
    )
    destination_account_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("accounts.id", ondelete="CASCADE")
    )

    # Transaction Details
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(15, 6), default=Decimal("1.0"), server_default="1.0"
    )

    # Transaction Info
    date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payee: Mapped[str | None] = mapped_column(String(255))
    reference_number: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    # Tags and Categorization
    tags: Mapped[List[str] | None] = mapped_column(ARRAY(Text))

    # Reconciliation
    is_reconciled: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )
    reconciled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Recurring Transaction Link
    recurring_transaction_id: Mapped[int | None] = mapped_column(BigInteger)

    # Import Information
    external_id: Mapped[str | None] = mapped_column(String(255))
    import_source: Mapped[str | None] = mapped_column(String(50))

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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    account: Mapped["Account"] = relationship(
        "Account", back_populates="transactions", foreign_keys=[account_id]
    )
    destination_account: Mapped["Account | None"] = relationship(
        "Account",
        back_populates="destination_transactions",
        foreign_keys=[destination_account_id],
    )
    category: Mapped["Category | None"] = relationship(
        "Category", back_populates="transactions"
    )

    # Table Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')", name="chk_transaction_type"
        ),
        CheckConstraint("amount > 0", name="chk_amount_positive"),
        CheckConstraint(
            "type != 'transfer' OR destination_account_id IS NOT NULL",
            name="chk_transfer_has_destination",
        ),
        CheckConstraint(
            "account_id != destination_account_id", name="chk_no_self_transfer"
        ),
        CheckConstraint("exchange_rate > 0", name="chk_exchange_rate_positive"),
        Index(
            "idx_transactions_user_id", "user_id", postgresql_where="deleted_at IS NULL"
        ),
        Index(
            "idx_transactions_account_id",
            "account_id",
            postgresql_where="deleted_at IS NULL",
        ),
        Index("idx_transactions_category_id", "category_id"),
        Index("idx_transactions_date", "date", postgresql_ops={"date": "DESC"}),
        Index("idx_transactions_type", "type"),
        Index(
            "idx_transactions_created_at",
            "created_at",
            postgresql_ops={"created_at": "DESC"},
        ),
        Index("idx_transactions_payee", "payee", postgresql_where="payee IS NOT NULL"),
        Index("idx_transactions_tags", "tags", postgresql_using="gin"),
        Index(
            "idx_transactions_external_id",
            "external_id",
            postgresql_where="external_id IS NOT NULL",
        ),
        # Composite indexes for common query patterns
        Index(
            "idx_transactions_user_date",
            "user_id",
            "date",
            postgresql_ops={"date": "DESC"},
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "idx_transactions_account_date",
            "account_id",
            "date",
            postgresql_ops={"date": "DESC"},
            postgresql_where="deleted_at IS NULL",
        ),
        Index(
            "idx_transactions_user_type_date",
            "user_id",
            "type",
            "date",
            postgresql_ops={"date": "DESC"},
            postgresql_where="deleted_at IS NULL",
        ),
    )

    # Validators
    @validates("amount")
    def validate_amount(self, key, amount):
        """Validate that amount is positive."""
        if amount is not None and amount <= 0:
            raise ValueError("Transaction amount must be positive")
        return amount

    @validates("exchange_rate")
    def validate_exchange_rate(self, key, rate):
        """Validate that exchange rate is positive."""
        if rate is not None and rate <= 0:
            raise ValueError("Exchange rate must be positive")
        return rate

    @validates("type")
    def validate_type(self, key, transaction_type):
        """Validate transaction type."""
        valid_types = ["income", "expense", "transfer"]
        if transaction_type and transaction_type not in valid_types:
            raise ValueError(
                f"Transaction type must be one of: {', '.join(valid_types)}"
            )
        return transaction_type

    @validates("currency")
    def validate_currency(self, key, currency):
        """Validate currency code format."""
        if currency and len(currency) != 3:
            raise ValueError("Currency code must be exactly 3 characters")
        return currency.upper() if currency else currency

    @validates("description")
    def validate_description(self, key, description):
        """Validate that description is not empty."""
        if description and not description.strip():
            raise ValueError("Description cannot be empty or whitespace")
        return description.strip() if description else description

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, type='{self.type}', amount={self.amount})>"
