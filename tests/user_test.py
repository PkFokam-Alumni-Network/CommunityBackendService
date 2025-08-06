from fastapi.testclient import TestClient
from schemas.user_schema import (
    UserCreatedResponse,
    UserLoginResponse,
    UserGetResponse,
    UserGetResponseInternal,
)
from utils.func_utils import verify_jwt
from pydantic import TypeAdapter
from typing import List


def test_correct_login(client: TestClient) -> None:
    user_data = {
        "email": "login_test@example.com",
        "first_name": "Login",
        "last_name": "User",
        "password": "testpassword",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    login_data = {"email": "login_test@example.com", "password": "testpassword"}
    response = client.post("/login/", json=login_data)
    assert response.status_code == 200
    login_response: UserLoginResponse = UserLoginResponse.model_validate(response.json())

    assert login_response.access_token is not None
    assert login_response.token_type == "bearer"
    access_token = login_response.access_token
    payload = verify_jwt(access_token)
    assert payload is not None
    assert payload["user_id"] == user_data["email"]


def test_bad_login(client: TestClient) -> None:
    user_data = {
        "email": "bad_login_test@example.com",
        "first_name": "BadLogin",
        "last_name": "User",
        "password": "correctpassword",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    bad_login_data = {
        "email": "bad_login_test@example.com",
        "password": "wrongpassword",
    }
    response = client.post("/login/", json=bad_login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_get_all_users(client: TestClient) -> None:
    users_data = [
        {
            "email": "test_email1@example.com",
            "first_name": "Test1",
            "last_name": "User1",
            "password": "securepassword",
        },
        {
            "email": "test_email2@example.com",
            "first_name": "Test2",
            "last_name": "User2",
            "password": "anothersecurepassword",
        },
    ]
    for user in users_data:
        response = client.post("/users/", json=user)
        assert response.status_code == 201

    response = client.get("/users/")
    assert response.status_code == 200
    users = TypeAdapter(List[UserGetResponse]).validate_python(response.json())
    assert isinstance(users, list)
    assert len(users) == len(users_data)

    for i, user in enumerate(users_data):
        assert users[i].email == user["email"]
        assert users[i].first_name == user["first_name"]
        assert users[i].last_name == user["last_name"]


def test_create_get_user(client: TestClient) -> None:
    response = client.post(
        "/users/",
        json={
            "email": "test_email@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "graduation_year": 2023,
            "degree": "B.Sc.",
            "major": "Computer Science",
            "phone": "1234567890",
            "password": "securepassword",
            "current_occupation": "Engineer",
            "image": "test_image_url",
            "linkedin_profile": "https://linkedin.com/in/test",
        },
    )
    assert response.status_code == 201
    user: UserCreatedResponse = UserCreatedResponse.model_validate(response.json())
    assert user.email == "test_email@example.com"

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200
    user_response: UserGetResponse = UserGetResponse.model_validate(response.json())
    assert user_response.email == "test_email@example.com"


def test_get_non_existing_user(client: TestClient) -> None:
    response = client.get("/users/2")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_create_user_duplicate(client: TestClient) -> None:
    data = {
        "email": "test_email@example.com",
        "first_name": "Duplicate",
        "last_name": "User",
        "password": "securepassword",
    }
    response = client.post("/users/", json=data)
    assert response.status_code == 201
    response = client.post("/users/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exists."


def test_delete_existing_user(client: TestClient) -> None:
    response = client.post(
        "/users/",
        json={
            "email": "delete@example.com",
            "first_name": "Delete",
            "last_name": "User",
            "password": "securepassword",
        },
    )
    assert response.status_code == 201
    user = response.json()
    response = client.delete(f"/users/{user['id']}")
    assert response.status_code == 200
    response = client.delete(f"/users/{user['id']}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User does not exist."


# TODO: Uncomment and implement this test when the mentor assignment feature with id is implemented
# def test_assign_mentor(client: TestClient) -> None:
#     mentor_response = client.post("/users/", json={
#         "first_name": "Mentor",
#         "last_name": "User",
#         "password": "securepassword",
#     })
#     assert mentor_response.status_code == 201
#     mentee_response = client.post("/users/", json={
#         "email": "mentee@example.com",
#         "first_name": "Mentee",
#         "last_name": "User",
#         "password": "securepassword",
#     })
#     assert mentee_response.status_code == 201
#     mentee: UserGetResponse = UserGetResponse.model_validate(mentee_response.json())
#     user_id = mentee.id

#     response = client.put(f"/users/{user_id}", json={"mentor_email": mentor_email})
#     assert response.status_code == 200
#     updated = client.get(f"/users/{user_id}").json()
#     assert updated["mentor_email"] == mentor_email


def test_update_user(client: TestClient) -> None:
    user_data = {
        "email": "testuser@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "securepassword123",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user = response.json()
    update_data = {"first_name": "UpdatedJohn"}
    response = client.put(f"/users/{user['id']}", json=update_data)
    assert response.status_code == 200
    updated_user = UserGetResponse.model_validate(response.json())
    assert updated_user.first_name == "UpdatedJohn"


def test_update_user_email(client: TestClient) -> None:
    user_data = {
        "email": "update_email_test@example.com",
        "first_name": "Email",
        "last_name": "Update",
        "password": "securepassword",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user = response.json()
    new_email = "new_email@example.com"
    response = client.put(
        f"/users/{user['id']}/update-email", json={"new_email": new_email}
    )
    assert response.status_code == 200
    updated_user: UserGetResponse = UserGetResponse.model_validate(response.json())
    assert updated_user.email == new_email


def test_update_user_password(client: TestClient) -> None:
    user_data = {
        "email": "update_password_test@example.com",
        "first_name": "Password",
        "last_name": "Update",
        "password": "oldpassword",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user = response.json()
    update_password_data = {
        "old_password": "oldpassword",
        "new_password": "newsecurepassword",
    }
    response = client.put(
        f"/users/{user['id']}/update-password", json=update_password_data
    )
    assert response.status_code == 200
    login_data = {"email": user["email"], "password": "newsecurepassword"}
    response = client.post("/login/", json=login_data)
    assert response.status_code == 200
    loginResponse: UserLoginResponse = UserLoginResponse.model_validate(response.json())
    assert loginResponse.access_token is not None
    assert loginResponse.token_type == "bearer"


def test_get_user_count(client: TestClient) -> None:
    users_data = [
        {
            "email": "test_email1@example.com",
            "first_name": "Test1",
            "last_name": "User1",
            "password": "securepassword",
        },
        {
            "email": "test_email2@example.com",
            "first_name": "Test2",
            "last_name": "User2",
            "password": "securepassword",
        },
    ]
    for user in users_data:
        response = client.post("/users/", json=user)
        assert response.status_code == 201
    response = client.get("/users/?counts=true")
    assert response.status_code == 200
    assert response.json()["count"] == len(users_data)


def test_get_active_users(client: TestClient) -> None:
    users_data = [
        {
            "email": "active1@example.com",
            "first_name": "Active",
            "last_name": "User1",
            "password": "123",
            "is_active": True,
        },
        {
            "email": "active2@example.com",
            "first_name": "Active",
            "last_name": "User2",
            "password": "123",
            "is_active": True,
        },
        {
            "email": "inactive1@example.com",
            "first_name": "Inactive",
            "last_name": "User1",
            "password": "123",
            "is_active": False,
        },
    ]
    for user in users_data:
        response = client.post("/users/", json=user)
        assert response.status_code == 201

    response = client.get("/users/?active=true")
    assert response.status_code == 200
    active_users = TypeAdapter(List[UserGetResponseInternal]).validate_python(
        response.json()
    )
    assert len(active_users) == 2
    assert all(user.is_active for user in active_users)
    response = client.get("/users/?counts=true&active=true")
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_get_all_users_filters_by_name(client: TestClient) -> None:
    users_data = [
        {
            "email": "ella@example.com",
            "first_name": "Ella",
            "last_name": "Smith",
            "password": "secure",
        },
        {
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "secure",
        },
    ]
    for user in users_data:
        response = client.post("/users/", json=user)
        assert response.status_code == 201

    response = client.get("/users/")
    assert response.status_code == 200
    users = TypeAdapter(List[UserGetResponse]).validate_python(response.json())
    assert len(users) == 1
    assert users[0].first_name == "Ella"
    
def test_create_user_with_multiple_degrees(client: TestClient) -> None:
    user_data = {
        "email": "multi_degrees@example.com",
        "first_name": "Multi",
        "last_name": "DegreeUser",
        "password": "securepassword",
        "degrees": [
            {
                "degree_level": "BSc",
                "major": "Computer Science",
                "graduation_year": 2020,
                "university": "KSU"
            },
            {
                "degree_level": "MSc",
                "major": "Data Science",
                "graduation_year": 2022,
                "university": "MIT"
            }
        ]
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    user = response.json()
    assert len(user["degrees"]) == 2
    assert user["degrees"][0]["degree_level"] == "BSc"
