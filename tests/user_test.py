import pytest
from typing import Generator
from fastapi.testclient import TestClient
from models.user import User
from tests.test_fixtures import create_and_teardown_tables, client
from utils.func_utils import verify_jwt

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db() -> Generator[TestClient, None, None]:
    yield from create_and_teardown_tables(User.metadata)


def test_correct_login() -> None:
    user_data = {
        "email": "login_test@example.com",
        "first_name": "Login",
        "last_name": "User",
        "password": "testpassword",
        "graduation_year": 2023,
        "degree": "B.Sc.",
        "major": "Computer Science",
        "phone": "1234567890",
        "current_occupation": "Engineer",
        "image": "test_image_url",
        "linkedin_profile": "https://linkedin.com/in/test"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    login_data = {
        "email": "login_test@example.com",
        "password": "testpassword"
    }
    response = client.post("/login/", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    access_token = response.json()["access_token"]
    payload = verify_jwt(access_token)
    assert payload is not None
    assert payload["user_id"] == user_data["email"]


def test_bad_login() -> None:
    user_data = {
        "email": "bad_login_test@example.com",
        "first_name": "BadLogin",
        "last_name": "User",
        "password": "correctpassword",
        "graduation_year": 2023,
        "degree": "B.Sc.",
        "major": "Computer Science",
        "phone": "1234567890",
        "current_occupation": "Engineer",
        "image": "test_image_url",
        "linkedin_profile": "https://linkedin.com/in/test"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    bad_login_data = {
        "email": "bad_login_test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login/", json=bad_login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"



def test_get_users() -> None:
    users_data = [
        {
            "email": "test_email1@example.com",
            "first_name": "Test1",
            "last_name": "User1",
            "graduation_year": 2023,
            "degree": "B.Sc.",
            "major": "Computer Science",
            "phone": "1234567890",
            "password": "securepassword",
            "current_occupation": "Engineer",
            "image": "test_image_url1",
            "linkedin_profile": "https://linkedin.com/in/test1"
        },
        {
            "email": "test_email2@example.com",
            "first_name": "Test2",
            "last_name": "User2",
            "graduation_year": 2024,
            "degree": "M.Sc.",
            "major": "Data Science",
            "phone": "0987654321",
            "password": "anothersecurepassword",
            "current_occupation": "Data Analyst",
            "image": "test_image_url2",
            "linkedin_profile": "https://linkedin.com/in/test2"
        }
    ]

    for user in users_data:
        response = client.post("/users/", json=user)
        assert response.status_code == 201
        assert response.json()["email"] == user["email"]

    response = client.get("/users/")
    assert response.status_code == 200

    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == len(users_data)

    for i, user in enumerate(users_data):
        assert response_data[i]["email"] == user["email"]
        assert response_data[i]["first_name"] == user["first_name"]
        assert response_data[i]["last_name"] == user["last_name"]


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
    assert email == "test_email@example.com"

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
    assign_mentor_response = client.put(f"/users/{mentee_email}",
        json={
            "mentor_email": mentor_email
        }            
    ) 
    assert assign_mentor_response.status_code == 200
    mentee_updated = client.get(f"/users/{mentee_email}")
    assert mentee_updated.status_code == 200
    mentee_updated_data = mentee_updated.json()
    assert mentee_updated_data["mentor_email"] == mentor_email
    

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

