"""Initial migration with all models, indexes, and constraints

Revision ID: 7aef2452f710
Revises: 
Create Date: 2025-11-12 14:16:28.174553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7aef2452f710'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
