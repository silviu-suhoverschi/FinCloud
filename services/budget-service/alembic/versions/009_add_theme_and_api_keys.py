"""Add theme preference and API keys management

Revision ID: 009_add_theme_and_api_keys
Revises: 8b3e94f12a11
Create Date: 2025-11-15 19:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "009_add_theme_and_api_keys"
down_revision = "8b3e94f12a11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add theme column to users table
    op.add_column(
        "users",
        sa.Column("theme", sa.String(length=20), server_default="auto", nullable=True),
    )
    op.execute("UPDATE users SET theme = 'auto' WHERE theme IS NULL")
    op.alter_column("users", "theme", nullable=False)
    op.create_check_constraint(
        "chk_theme_valid", "users", "theme IN ('light', 'dark', 'auto')"
    )

    # Create api_keys table
    op.create_table(
        "api_keys",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
        sa.Column("key_prefix", sa.String(length=10), nullable=False),
        sa.Column("permissions", sa.Text(), server_default="read", nullable=True),
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_hash"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("idx_api_keys_is_active", "api_keys", ["is_active"])
    op.create_index("idx_api_keys_key_hash", "api_keys", ["key_hash"])
    op.create_index("idx_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index(op.f("ix_api_keys_id"), "api_keys", ["id"])


def downgrade() -> None:
    # Drop api_keys table
    op.drop_index(op.f("ix_api_keys_id"), table_name="api_keys")
    op.drop_index("idx_api_keys_user_id", table_name="api_keys")
    op.drop_index("idx_api_keys_key_hash", table_name="api_keys")
    op.drop_index("idx_api_keys_is_active", table_name="api_keys")
    op.drop_table("api_keys")

    # Remove theme column from users table
    op.drop_constraint("chk_theme_valid", "users", type_="check")
    op.drop_column("users", "theme")
