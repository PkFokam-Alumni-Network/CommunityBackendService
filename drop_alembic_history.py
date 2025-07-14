'''
This file drops the alembic history in the database 
you want to facilitate the migration of you changes
to the schema to be reflected on the database.
'''

from sqlalchemy import create_engine, text

# Set up your SQLite database connection
engine = create_engine("sqlite:///database.db")

# Run the DROP TABLE command
with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

print("---- Done ----")