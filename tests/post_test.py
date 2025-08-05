import pytest
from fastapi.testclient import TestClient
from models.user import User
from schemas.post_schema import PostResponse
from schemas.user_schema import UserCreatedResponse

@pytest.fixture(scope="function")
def test_users(client: TestClient) -> list[User]:
    user1_data = {
        "email":"alice@example.com",
        "first_name":"Alice",
        "last_name":"Test",
        "password":"pass123"
    }

    user2_data = {
        "email":"bob@example.com",
        "first_name":"Bob",
        "last_name":"Test",
        "password":"pass123"
    }

    user1 = UserCreatedResponse.model_validate(client.post("/users/", json=user1_data).json())
    user2 = UserCreatedResponse.model_validate(client.post("/users/", json=user2_data).json())

    return [user1, user2]


def test_create_get_post(client: TestClient,test_users: list[User]):
    user1 = test_users[0]
    post_data = {
        "title": "First Test Post",
        "content": "This is a test",
        "category": "General"
    }
    response = client.post("/posts/", json=post_data, params={"user_id": user1.id})
    assert response.status_code == 201

    new_post: PostResponse = PostResponse.model_validate(response.json())
    assert new_post.title == "First Test Post"
    assert new_post.content == "This is a test"
    assert new_post.author_id == user1.id

    response = client.get(f"/posts/{new_post.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "First Test Post"

def test_get_recent_posts(client: TestClient,test_users: list[User]):
    for i, user in enumerate(test_users, start=1):
        for category in ["Career", "Immigration", "Job search"]:
            post_response = client.post("/posts/", json={
                "title": f"Post {i}",
                "content": f"Content {i}",
                "category": f"{category}"
            }, params={"user_id": user.id})
            assert post_response.status_code == 201

    response = client.get("/posts/recent")
    assert response.status_code == 200
    assert len(response.json()) >= 6


def test_get_recent_posts_by_category(client: TestClient,test_users: list[User]):
    user1 = test_users[0]
    client.post("/posts/", json={
        "title": "Science Post",
        "content": "About science",
        "category": "Science"
    }, params={"user_id": user1.id})

    response = client.get("/posts/recent?category=Science")
    assert response.status_code == 200
    assert all(post["category"] == "Science" for post in response.json())


def test_get_non_existing_post(client: TestClient):
    response = client.get("/posts/999") 
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_update_post_success(client: TestClient,test_users: list[User]):
    user1 = test_users[0]
    post_data = {
        "title": "Update Me",
        "content": "Before update",
        "category": "News"
    }
    post = client.post("/posts/", json=post_data, params={"user_id": user1.id}).json()

    post_id = post["id"]
    update_post_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "category": "Tech"
    }
    response = client.put(f"/posts/{post_id}", json=update_post_data, params={"user_id": user1.id})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_post_unauthorized(client: TestClient,test_users: list[User]):
    user1, user2 = test_users
    post = client.post("/posts/", json={
        "title": "Unauthorized Edit",
        "content": "Don't touch",
        "category": "Privacy"
    }, params={"user_id": user1.id}).json()

    response = client.put(f"/posts/{post['id']}", json={
        "title": "Hacked!",
        "content": "Unauthorized",
        "category": "Hack"
    }, params={"user_id": user2.id})

    assert response.status_code == 401
    assert "Not authorized" in response.json()["detail"]


def test_delete_post_success(client: TestClient,test_users: list[User]):
    user1 = test_users[0]
    post = client.post("/posts/", json={
        "title": "Trash Me",
        "content": "This won't last",
        "category": "Temp"
    }, params={"user_id": user1.id}).json()

    post_id = post["id"]
    response = client.delete(f"/posts/{post_id}", params={"user_id": user1.id})
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]


def test_delete_post_unauthorized(client: TestClient,test_users: list[User]):
    user1, user2 = test_users
    post = client.post("/posts/", json={
        "title": "Do Not Delete",
        "content": "Mine only",
        "category": "Lock"
    }, params={"user_id": user1.id}).json()

    post_id = post["id"]
    response = client.delete(f"/posts/{post_id}", params={"user_id": user2.id})
    assert response.status_code == 401

