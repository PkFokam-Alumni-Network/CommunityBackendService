"""Create events and user_events tables

Revision ID: def456abc789
Revises: abc123def456
Create Date: 2025-05-21 04:15:14.317278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'def456abc789'
down_revision = 'abc123def456'
branch_labels = None
depends_on = None


def upgrade():
    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=False),
        sa.Column('location', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image', sa.Text(), nullable=True),
        sa.Column('categories', sa.Text()),
    )

    # Create user_events table
    op.create_table(
        'user_events',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade():
    op.drop_table('user_events')
    op.drop_table('events')
