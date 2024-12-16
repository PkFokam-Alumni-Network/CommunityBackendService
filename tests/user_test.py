import pytest
from typing import Generator
from fastapi.testclient import TestClient
from models.user import User
from tests.test_fixtures import create_and_teardown_tables, client


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db() -> Generator[TestClient, None, None]:
    yield from create_and_teardown_tables(User.metadata)

def test_create_get_user() -> None:
    response = client.post(
        "/users/",
        json={
            "email": "test_email@example.com",
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
    assert response.status_code == 201
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

def test_update_user():
    user_data = {
        "email": "testuser@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "securepassword123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user = response.json()

    update_data = {"first_name": "UpdatedJohn"}
    email = user['email']
    response = client.put(f"/users/{email}", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["first_name"] == "UpdatedJohn"
    assert updated_user["last_name"] == "Doe"

