"""add_degrees_table_and_migrate_data

Revision ID: ed741c313f00
Revises: 695b6fad5fda
Create Date: 2025-05-19 15:40:45.213627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey


# revision identifiers, used by Alembic.
revision: str = 'ed741c313f00'
down_revision: Union[str, None] = '695b6fad5fda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Create temporary models
metadata_obj = sa.MetaData()
TempBase = declarative_base(metadata=metadata_obj)

class TempUser(TempBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String)
    degree = Column(String)
    major = Column(String)
    graduation_year = Column(Integer)

class TempDegree(TempBase):
    __tablename__ = "degrees"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    degree = Column(String, nullable=False)
    major = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=False)
    location = Column(String, nullable=False)

def upgrade() -> None:
    # Create degrees table
    op.create_table(
        "degrees",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("degree", sa.String, nullable=False),
        sa.Column("major", sa.String, nullable=False),
        sa.Column("graduation_year", sa.Integer, nullable=False),
        sa.Column("location", sa.String, nullable=False),
    )

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # Migrate data from users table to degrees table
    users = session.query(TempUser).filter(TempUser.degree.isnot(None)).all()

    # Populate degrees table
    for user in users:
        degree = TempDegree(
            user_id=user.id,
            degree=user.degree,
            major=user.major or "Not Specified",
            graduation_year=user.graduation_year or 0,
            location="Not Specified"  # Default value for location
        )
        session.add(degree)

    # Commit changes and close session
    session.commit()
    session.close()

def downgrade() -> None:
     # Drop the degrees table
    op.drop_table('degrees')
    # Note: The downgrade function does not need to handle data migration back to the users table