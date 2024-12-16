import tempfile
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from main import app
from database import get_db
from models.user import User

def override_get_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown_db() -> Generator[TestClient, None, None]:
    User.metadata.create_all(bind=engine)
    yield client
    app.dependency_overrides.clear()
    User.metadata.drop_all(bind=engine)  
    engine.dispose()
     
temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{temp_db_file.name}"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)

app.dependency_overrides[get_db] = override_get_db
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
client = TestClient(app)

def test_create_get_user() -> None:
    response = client.post(
        "/users/",
        json={
            "email": "test_email@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "None",
            "graduation_year": 2023,
            "degree": "B.Sc.",
            "major": "Computer Science",
            "phone": "1234567890",
            "password": "securepassword",
            "current_occupation": "Engineer",
            "image": "test_image_url",
            "linkedin_profile": "https://linkedin.com/in/test",
            "mentor_email": "test_email1@example.com",
        },
    )
    assert response.status_code == 201
    email: str = response.json()["email"]
    assert  email == "test_email@example.com"

    response = client.get(f"/users/{email}")
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_get_non_existing_user() -> None:
    response = client.get("/users/fake_email")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_create_user_duplicate() -> None:
    response = client.post(
        "/users/",
        json={
            "email": "test_email@example.com",
            "first_name": "Duplicate",
            "last_name": "User",
            "password": "securepassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exists."

def test_delete_existing_user() -> None:
    create_response = client.post(
        "/users/",
        json={
            "email": "delete@example.com",
            "first_name": "Delete",
            "last_name": "User",
            "password": "securepassword",
        },
    )
    assert create_response.status_code == 201  
    new_user = create_response.json()
    user_email = new_user["email"]
    delete_route = f"/users/{user_email}" 
    delete_response = client.delete(delete_route)
    assert delete_response.status_code == 200 
    delete_response = client.delete(delete_route)
    assert delete_response.status_code == 404  
    assert delete_response.json()["detail"] == "User does not exist."

def test_assign_mentor() -> None:
    mentor_response = client.post(
        "/users/",
        json={
            "email": "mentor@example.com",
            "first_name": "Mentor",
            "last_name": "User",
            "password": "securepassword",
        },
    )
    assert mentor_response.status_code == 201
    mentor_data = mentor_response.json()
    mentor_email = mentor_data["email"]
    mentee_response = client.post(
        "/users/",
        json={
            "email": "mentee@example.com",
            "first_name": "Mentee",
            "last_name": "User",
            "password": "securepassword",
        },
    )
    assert mentee_response.status_code == 201
    mentee_data = mentee_response.json()
    mentee_email = mentee_data["email"]
    assign_mentor_response = client.put(f"/users/",
        params={
            "mentor_email": mentor_email,
            "mentee_email": mentee_email
        }            
    ) 
    assert assign_mentor_response.status_code == 200
    assert "mentee with email" in assign_mentor_response.json()["message"]
    mentee_updated = client.get(f"/users/{mentee_email}")
    assert mentee_updated.status_code == 200
    mentee_updated_data = mentee_updated.json()
    assert mentee_updated_data["mentor_email"] == mentor_email
    
