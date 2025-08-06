"""Create users table

Revision ID: abc123def456
Revises: 
Create Date: 2025-05-20 04:15:14.317278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.Text(), nullable=False, index=True, unique=True),
        sa.Column('first_name', sa.Text(), nullable=False),
        sa.Column('last_name', sa.Text(), nullable=False),
        sa.Column('password', sa.Text(), nullable=False),
        sa.Column('address', sa.Text()),
        sa.Column('phone', sa.Text()),
        sa.Column('image', sa.Text(), nullable=True),
        sa.Column('bio', sa.Text()),
        sa.Column('graduation_year', sa.Integer()),
        sa.Column('degree', sa.Text()),
        sa.Column('major', sa.Text()),
        sa.Column('current_occupation', sa.Text()),
        sa.Column('mentor_email', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('linkedin_profile', sa.Text()),
        sa.Column('instagram_profile', sa.Text(), nullable=True),
        sa.Column('role', sa.Text(), nullable=False),
    )


def downgrade():
    op.drop_table('users')