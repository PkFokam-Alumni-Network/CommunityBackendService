from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = None
SessionLocal = None

def init_db(database_url: str):
    global engine, SessionLocal
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    from database import SessionLocal  # ensure it's set
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
