"""remove_redundant_degree_columns_from_users

Revision ID: a865f90d3d05
Revises: ed741c313f00
Create Date: 2025-05-19 16:05:41.520197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a865f90d3d05'
down_revision: Union[str, None] = 'ed741c313f00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
