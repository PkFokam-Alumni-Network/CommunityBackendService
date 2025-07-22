import os
import tempfile
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from main import app
import core.database as database

@pytest.fixture(scope="session")
def temp_db_url() -> Generator[str, None, None]:
    """Creates a temp SQLite DB file and cleans it up after the session."""
    tmpfile = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tmpfile.name
    tmpfile.close()
    db_url = f"sqlite:///{db_path}"
    yield db_url
    try:
        os.unlink(db_path)
    except PermissionError:
        print(f"Could not delete temp file {db_path}, it might still be in use.")


@pytest.fixture(scope="function")
def engine(temp_db_url: str):
    test_engine = create_engine(temp_db_url, connect_args={"check_same_thread": False})
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
