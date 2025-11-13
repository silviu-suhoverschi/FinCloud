"""Add role field to users table

Revision ID: 8b3e94f12a11
Revises: 7aef2452f710
Create Date: 2025-11-12 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b3e94f12a11"
down_revision: Union[str, None] = "7aef2452f710"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add role field to users table."""
    # Add role column
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
    )

    # Add check constraint for valid roles
    op.create_check_constraint(
        "chk_role_valid", "users", "role IN ('user', 'admin', 'premium')"
    )

    # Add index on role column
    op.create_index("idx_users_role", "users", ["role"])


def downgrade() -> None:
    """Remove role field from users table."""
    # Drop index
    op.drop_index("idx_users_role", table_name="users")

    # Drop check constraint
    op.drop_constraint("chk_role_valid", "users", type_="check")

    # Drop column
    op.drop_column("users", "role")
