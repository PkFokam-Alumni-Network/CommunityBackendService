import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from main import app
import core.database as database

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://user:password@postgres:5432/test_db")


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
    database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
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
