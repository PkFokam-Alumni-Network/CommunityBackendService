"""Add support for multiple degrees

Revision ID: faccf920de79
Revises: 81d1bcd3be5c
Create Date: 2025-10-26 15:59:34.125980

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'faccf920de79'
down_revision: Union[str, None] = '81d1bcd3be5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the new degrees JSONB column (nullable for now)
    op.add_column('users', sa.Column('degrees', JSONB, nullable=True))
    
    # Migrate existing data to the new structure
    # This uses a raw SQL query to handle the JSONB structure properly
    connection = op.get_bind()
    
    # Build JSONB array from existing fields
    connection.execute(text("""
        UPDATE users
        SET degrees = CASE
            WHEN degree IS NOT NULL OR major IS NOT NULL OR graduation_year IS NOT NULL
            THEN jsonb_build_array(
                jsonb_build_object(
                    'degree', COALESCE(degree, ''),
                    'major', COALESCE(major, ''),
                    'graduation_year', graduation_year,
                    'university', ''
                )
            )
            ELSE '[]'::jsonb
        END
    """))
    
    # Now that data is migrated, we can drop the old columns
    # Comment these out if you want to keep them temporarily for safety
    op.drop_column('users', 'degree')
    op.drop_column('users', 'major')


def downgrade():
    # Recreate the old columns
    op.add_column('users', sa.Column('major', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('degree', sa.Text(), nullable=True))
    
    # Migrate data back (take first degree from array)
    connection = op.get_bind()
    connection.execute(text("""
        UPDATE users
        SET 
            degree = CASE 
                WHEN jsonb_array_length(degrees) > 0 
                THEN degrees->0->>'degree'
                ELSE NULL
            END,
            major = CASE 
                WHEN jsonb_array_length(degrees) > 0 
                THEN degrees->0->>'major'
                ELSE NULL
            END
        WHERE degrees IS NOT NULL
    """))
    
    # Drop the JSONB column
    op.drop_column('users', 'degrees')