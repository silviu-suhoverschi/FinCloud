"""Initial migration with all models, indexes, and constraints

Revision ID: d7c5a96c7c14
Revises:
Create Date: 2025-11-12 14:16:44.793206

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "d7c5a96c7c14"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
