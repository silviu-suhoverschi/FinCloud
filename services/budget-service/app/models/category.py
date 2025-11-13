from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Integer,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction
    from app.models.budget import Budget
    from app.models.recurring_transaction import RecurringTransaction

"""
Category Model

Transaction categories with hierarchical support (parent-child relationships).
"""


class Category(Base):
    """Category model for transaction categorization."""

    __tablename__ = "categories"

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
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE")
    )

    # Category Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Visual Properties
    color: Mapped[str | None] = mapped_column(String(7))
    icon: Mapped[str | None] = mapped_column(String(50))

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
    user: Mapped["User"] = relationship("User", back_populates="categories")
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="category"
    )
    budgets: Mapped[List["Budget"]] = relationship(
        "Budget",
        back_populates="category",
        cascade="all, delete-orphan"
    )
    recurring_transactions: Mapped[List["RecurringTransaction"]] = relationship(
        "RecurringTransaction",
        back_populates="category"
    )

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", "parent_id", name="uq_user_category_name"),
        CheckConstraint(
            "type IN ('income', 'expense', 'transfer')",
            name="chk_category_type"
        ),
        CheckConstraint(
            "id != parent_id",
            name="chk_no_self_reference"
        ),
        Index("idx_categories_user_id", "user_id", postgresql_where="deleted_at IS NULL"),
        Index("idx_categories_parent_id", "parent_id"),
        Index("idx_categories_type", "type"),
        Index("idx_categories_sort_order", "sort_order"),
        # Composite indexes for common query patterns
        Index("idx_categories_user_type_active", "user_id", "type", "is_active", postgresql_where="deleted_at IS NULL"),
        Index("idx_categories_user_parent", "user_id", "parent_id", postgresql_where="deleted_at IS NULL"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', type='{self.type}')>"
