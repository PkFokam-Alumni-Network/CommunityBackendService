import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv(dotenv_path=".database_url.example")
DATABASE_URL = os.getenv("DATABASE_URL",f"sqlite:///{tempfile.NamedTemporaryFile(suffix='.db', delete=False).name}")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set!")


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()