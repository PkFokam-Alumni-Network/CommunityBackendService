from fastapi.testclient import TestClient

def _create_user_and_login(client: TestClient, email="session_test@example.com"):
    user_data = {
        "email": email,
        "first_name": "Session",
        "last_name": "Tester",
        "password": "securepassword",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    response = client.post("/login/", json={"email": email, "password": "securepassword"})
    assert response.status_code == 200
    cookies = response.cookies
    assert "session_token" in cookies
    return cookies.get("session_token"), email

def test_session_created_on_login(client: TestClient):
    token, _ = _create_user_and_login(client)
    assert token is not None
