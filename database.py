from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.retry import retry_on_db_error

Base = declarative_base()
engine = None
SessionLocal = None

@retry_on_db_error()
def init_db(database_url: str):
    global engine, SessionLocal
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=900, # 15 minutes
        pool_timeout=30,
        pool_size=10,
        max_overflow=20,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    from database import SessionLocal  # ensure it's set
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
    finally:
        db.close()
