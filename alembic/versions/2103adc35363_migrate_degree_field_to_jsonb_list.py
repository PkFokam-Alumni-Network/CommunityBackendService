"""migrate degree field to jsonb list

Revision ID: 2103adc35363
Revises: 7dc36ecb2bc8
Create Date: 2025-07-21 20:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = '2103adc35363'
down_revision = '7dc36ecb2bc8'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add new degrees column
    op.add_column('users', sa.Column('degrees', JSONB(astext_type=sa.Text()), nullable=True))

    # 2. Copy data from old fields into new JSONB field
    op.execute("""
        UPDATE users SET degrees = jsonb_build_array(
            jsonb_build_object(
                'degree_level', degree,
                'major', major,
                'graduation_year', graduation_year,
                'university', 'Unknown University'
            )
        )
        WHERE degree IS NOT NULL
    """)

    # 3. OPTIONAL: Drop old fields (only if you’re sure everything migrated)
    # op.drop_column('users', 'degree')
    # op.drop_column('users', 'major')
    # op.drop_column('users', 'graduation_year')


def downgrade():
    # Add back old columns if needed
    op.add_column('users', sa.Column('degree', sa.String(), nullable=True))
    op.add_column('users', sa.Column('major', sa.String(), nullable=True))
    op.add_column('users', sa.Column('graduation_year', sa.Integer(), nullable=True))

    # Pull back data from JSONB
    op.execute("""
        UPDATE users
        SET
            degree = degrees->0->>'degree_level',
            major = degrees->0->>'major',
            graduation_year = (degrees->0->>'graduation_year')::integer
        WHERE degrees IS NOT NULL
    """)

    # Drop degrees field
    op.drop_column('users', 'degrees')
