import pytest
from fastapi.testclient import TestClient
from models.user import User
from schemas.post_schema import PostResponse
from schemas.user_schema import UserCreatedResponse

@pytest.fixture(scope="function")
def test_users(client: TestClient) -> list[tuple[User, str]]:
    """Create test users and return them with their session tokens"""
    user1_data = {
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Test",
        "password": "pass123"
    }

    user2_data = {
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Test",
        "password": "pass123"
    }


    user1_response = client.post("/users/", json=user1_data)
    user2_response = client.post("/users/", json=user2_data)
    
    user1 = UserCreatedResponse.model_validate(user1_response.json())
    user2 = UserCreatedResponse.model_validate(user2_response.json())

    login1_response = client.post("/login", json={
        "email": "alice@example.com",
        "password": "pass123"
    })
    login2_response = client.post("/login", json={
        "email": "bob@example.com",
        "password": "pass123"
    })

    token1 = login1_response.cookies.get("session_token")
    token2 = login2_response.cookies.get("session_token")

    return [(user1, token1), (user2, token2)]


def test_create_get_post(client: TestClient, test_users: list[tuple[User, str]]):
    user1, token1 = test_users[0]
    
    post_data = {
        "title": "First Test Post",
        "content": "This is a test",
        "category": "General"
    }
    
    # Set cookie in request
    response = client.post(
        "/posts/",
        json=post_data,
        cookies={"session_token": token1}
    )
    assert response.status_code == 201

    new_post: PostResponse = PostResponse.model_validate(response.json())
    assert new_post.title == "First Test Post"
    assert new_post.content == "This is a test"
    assert new_post.author_id == user1.id

    response = client.get(f"/posts/{new_post.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "First Test Post"


def test_create_post_without_authentication(client: TestClient):
    post_data = {
        "title": "Unauthorized Post",
        "content": "This should fail",
        "category": "General"
    }
    
    response = client.post("/posts/", json=post_data)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_recent_posts(client: TestClient, test_users: list[tuple[User, str]]):
    for i, (_, token) in enumerate(test_users, start=1):
        for category in ["Career", "Immigration", "Job search"]:
            post_response = client.post(
                "/posts/",
                json={
                    "title": f"Post {i}",
                    "content": f"Content {i}",
                    "category": f"{category}"
                },
                cookies={"session_token": token}
            )
            assert post_response.status_code == 201

    response = client.get("/posts/recent")
    assert response.status_code == 200
    assert len(response.json()) >= 6


def test_get_recent_posts_by_category(client: TestClient, test_users: list[tuple[User, str]]):
    _, token1 = test_users[0]
    
    client.post(
        "/posts/",
        json={
            "title": "Science Post",
            "content": "About science",
            "category": "Science"
        },
        cookies={"session_token": token1}
    )

    response = client.get("/posts/recent?category=Science")
    assert response.status_code == 200
    assert all(post["category"] == "Science" for post in response.json())


def test_get_non_existing_post(client: TestClient):
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_update_post_success(client: TestClient, test_users: list[tuple[User, str]]):
    _, token1 = test_users[0]
    
    post_data = {
        "title": "Update Me",
        "content": "Before update",
        "category": "News"
    }
    post = client.post(
        "/posts/",
        json=post_data,
        cookies={"session_token": token1}
    ).json()

    post_id = post["id"]
    update_post_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "category": "Tech"
    }
    response = client.put(
        f"/posts/{post_id}",
        json=update_post_data,
        cookies={"session_token": token1}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_post_unauthorized(client: TestClient, test_users: list[tuple[User, str]]):
    (_, token1), (_, token2) = test_users
    
    post = client.post(
        "/posts/",
        json={
            "title": "Unauthorized Edit",
            "content": "Don't touch",
            "category": "Privacy"
        },
        cookies={"session_token": token1}
    ).json()

    # User2 tries to update user1's post
    response = client.put(
        f"/posts/{post['id']}",
        json={
            "title": "Hacked!",
            "content": "Unauthorized",
            "category": "Hack"
        },
        cookies={"session_token": token2}
    )

    assert response.status_code == 401
    assert "Not authorized" in response.json()["detail"]


def test_update_post_without_authentication(client: TestClient, test_users: list[tuple[User, str]]):
    _, token1 = test_users[0]
    
    post = client.post(
        "/posts/",
        json={
            "title": "Protected Post",
            "content": "Cannot edit without auth",
            "category": "Security"
        },
        cookies={"session_token": token1}
    ).json()

    # Try to update without authentication
    response = client.put(
        f"/posts/{post['id']}",
        json={
            "title": "Hacked!",
            "content": "Unauthorized",
            "category": "Hack"
        }
    )

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_delete_post_success(client: TestClient, test_users: list[tuple[User, str]]):
    _, token1 = test_users[0]
    
    post = client.post(
        "/posts/",
        json={
            "title": "Trash Me",
            "content": "This won't last",
            "category": "Temp"
        },
        cookies={"session_token": token1}
    ).json()

    post_id = post["id"]
    response = client.delete(
        f"/posts/{post_id}",
        cookies={"session_token": token1}
    )
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]


def test_delete_post_unauthorized(client: TestClient, test_users: list[tuple[User, str]]):
    (_, token1), (_, token2) = test_users
    
    post = client.post(
        "/posts/",
        json={
            "title": "Do Not Delete",
            "content": "Mine only",
            "category": "Lock"
        },
        cookies={"session_token": token1}
    ).json()

    post_id = post["id"]
    response = client.delete(
        f"/posts/{post_id}",
        cookies={"session_token": token2}
    )
    assert response.status_code == 401
    assert "Not authorized" in response.json()["detail"]


def test_delete_post_without_authentication(client: TestClient, test_users: list[tuple[User, str]]):
    _, token1 = test_users[0]
    
    post = client.post(
        "/posts/",
        json={
            "title": "Protected Post",
            "content": "Cannot delete without auth",
            "category": "Security"
        },
        cookies={"session_token": token1}
    ).json()

    response = client.delete(f"/posts/{post['id']}")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]