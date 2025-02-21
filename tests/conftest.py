import tempfile
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from main import app
from database import get_db

temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{temp_db_file.name}"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)

def override_get_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def create_and_teardown_tables(metadata) -> Generator[TestClient, None, None]:
    metadata.create_all(bind=engine)
    yield client
    metadata.drop_all(bind=engine)

def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    app.dependency_overrides.clear()