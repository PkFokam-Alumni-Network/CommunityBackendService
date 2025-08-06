"""Create announcements table

Revision ID: ghi789jkl012
Revises: def456abc789
Create Date: 2025-05-22 04:15:14.317278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ghi789jkl012'
down_revision = 'def456abc789'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'announcements',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.Text()),
        sa.Column('description', sa.Text()),
        sa.Column('announcement_date', sa.DateTime()),
        sa.Column('announcement_deadline', sa.DateTime(), nullable=True),
        sa.Column('image', sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table('announcements')
