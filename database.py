import os, tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

ENV = os.getenv("ENV", "development")
if ENV == "development":
    temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    DATABASE_URL = f"sqlite:///{temp_db_file.name}"
else:
    DATABASE_URL = "sqlite:////app/sql_database/database.db" 

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()