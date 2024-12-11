import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import Base
from main import app
from database import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def test_client():
    Base.metadata.create_all(bind=engine)
    # Run tests
    yield client
    # Drop the test database
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    os.remove("test.db")

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "graduation_year": 2023,
            "degree": "B.Sc.",
            "major": "Computer Science",
            "phone": "1234567890",
            "password": "securepassword",
            "current_occupation": "Engineer",
            "image": "test_image_url",
            "linkedin_profile": "https://linkedin.com/in/test"
        },
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_create_user_duplicate():
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "first_name": "Duplicate",
            "last_name": "User",
            "graduation_year": 2023,
            "degree": "B.Sc.",
            "major": "Computer Science",
            "phone": "1234567890",
            "password": "securepassword",
            "current_occupation": "Engineer",
            "image": "test_image_url",
            "linkedin_profile": "https://linkedin.com/in/duplicate"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
