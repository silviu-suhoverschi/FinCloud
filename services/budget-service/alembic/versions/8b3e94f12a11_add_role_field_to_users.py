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
    # Check if role column exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col["name"] for col in inspector.get_columns("users")]

    # Add role column only if it doesn't exist
    if "role" not in columns:
        op.add_column(
            "users",
            sa.Column("role", sa.String(length=20), server_default="user", nullable=False),
        )

    # Check if constraint exists
    constraints = [const["name"] for const in inspector.get_check_constraints("users")]
    if "chk_role_valid" not in constraints:
        # Add check constraint for valid roles
        op.create_check_constraint(
            "chk_role_valid", "users", "role IN ('user', 'admin', 'premium')"
        )

    # Check if index exists
    indexes = [idx["name"] for idx in inspector.get_indexes("users")]
    if "idx_users_role" not in indexes:
        # Add index on role column
        op.create_index("idx_users_role", "users", ["role"])


def downgrade() -> None:
    """Remove role field from users table."""
    # Check what exists before dropping
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Drop index if it exists
    indexes = [idx["name"] for idx in inspector.get_indexes("users")]
    if "idx_users_role" in indexes:
        op.drop_index("idx_users_role", table_name="users")

    # Drop check constraint if it exists
    constraints = [const["name"] for const in inspector.get_check_constraints("users")]
    if "chk_role_valid" in constraints:
        op.drop_constraint("chk_role_valid", "users", type_="check")

    # Drop column if it exists
    columns = [col["name"] for col in inspector.get_columns("users")]
    if "role" in columns:
        op.drop_column("users", "role")
