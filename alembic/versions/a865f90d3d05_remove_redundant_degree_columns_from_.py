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
    # Remove redundant columns from users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('degree')
        batch_op.drop_column('major')
        batch_op.drop_column('graduation_year')


def downgrade() -> None:
    # Add columns back if you need to roll back
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('degree', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('major', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('graduation_year', sa.Integer(), nullable=True))
