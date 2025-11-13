from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User

"""
Tag Model

Reusable tags for transactions and budgets.
"""


class Tag(Base):
    """Tag model for flexible categorization."""

    __tablename__ = "tags"

    # Primary Key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Tag Details
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7))
    usage_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tags")

    # Table Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag_name"),
        Index("idx_tags_user_id", "user_id"),
        Index("idx_tags_usage_count", "usage_count", postgresql_ops={"usage_count": "DESC"}),
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"
