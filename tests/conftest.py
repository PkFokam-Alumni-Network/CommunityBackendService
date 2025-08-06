import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from main import app
import database
from datetime import datetime, timezone, timedelta
from models.user import User
from utils.func_utils import get_password_hash
import core.database as database

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://user:password@localhost:5432/test_db"
)

@pytest.fixture(scope="session")
def db_url() -> str:
    """Provides the PostgreSQL test database URL."""
    return TEST_DATABASE_URL


@pytest.fixture(scope="function")
def engine(db_url: str):
    """Creates the PostgreSQL engine and initializes the schema."""
    test_engine = create_engine(db_url)
    database.Base.metadata.create_all(bind=test_engine)
    database.engine = test_engine
    database.SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    yield test_engine
    database.Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Creates a new SQLAlchemy session per test."""
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provides a test client with an isolated DB session."""

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
@pytest.fixture
def test_user(db_session):
    """Create a test user for session testing"""
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password=get_password_hash("testpassword123"),
        address="123 Test Street",
        phone="1234567890",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_session_data():
    """Sample session data for testing"""
    return {
        "token": "test_jwt_token_123",
        "device_type": "desktop",
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=24)
    }


