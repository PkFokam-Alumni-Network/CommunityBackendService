"""migrate degree field to JSON list

Revision ID: 2103adc35363
Revises: 7dc36ecb2bc8
Create Date: 2025-07-21 17:44:10.846292
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '2103adc35363'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Only modify the 'users' table

    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('users')]

    # Drop 'degree' column if it exists
    if 'degree' in columns:
        op.drop_column('users', 'degree')

    # Add 'degrees' JSON column
    op.add_column('users', sa.Column(
        'degrees',
        sa.JSON(),
        nullable=True,
    ))


def downgrade():
    op.drop_column('users', 'degrees')
    op.add_column('users', sa.Column('degree', sa.String(), nullable=True))
