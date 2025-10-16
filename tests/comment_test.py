import pytest
from fastapi.testclient import TestClient
from schemas.post_schema import PostResponse
from schemas.user_schema import UserCreatedResponse
from schemas.comment_schema import CommentResponse

@pytest.fixture(scope="function")
def test_users(client: TestClient) -> list:
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

    user1 = UserCreatedResponse.model_validate(client.post("/users/", json=user1_data).json())
    user2 = UserCreatedResponse.model_validate(client.post("/users/", json=user2_data).json())

    return [user1, user2]


@pytest.fixture(scope="function")
def test_post(client: TestClient, test_users: list) -> PostResponse:
    user1 = test_users[0]
    post_data = {
        "title": "Test Post for Comments",
        "content": "This post will have comments",
        "category": "Testing"
    }
    response = client.post("/posts/", json=post_data, params={"user_id": user1.id})
    return PostResponse.model_validate(response.json())


def test_create_comment(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    comment_data = {
        "content": "This is my first comment"
    }
    
    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id, "user_id": user1.id}
    )
    
    assert response.status_code == 201
    comment = CommentResponse.model_validate(response.json())
    assert comment.content == "This is my first comment"
    assert comment.post_id == test_post.id
    assert comment.author_id == user1.id


def test_get_comment(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    comment_data = {"content": "Retrieve me"}
    
    created_comment = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id, "user_id": user1.id}
    ).json()
    
    response = client.get(f"/comments/{created_comment['id']}")
    assert response.status_code == 200
    assert response.json()["content"] == "Retrieve me"


def test_get_comments_by_post(client: TestClient, test_users: list, test_post: PostResponse):
    user1, user2 = test_users
    
    # Create multiple comments
    client.post("/comments/", json={"content": "First comment"}, params={"post_id": test_post.id, "user_id": user1.id})
    client.post("/comments/", json={"content": "Second comment"}, params={"post_id": test_post.id, "user_id": user2.id})
    client.post("/comments/", json={"content": "Third comment"}, params={"post_id": test_post.id, "user_id": user1.id})
    
    response = client.get(f"/post/{test_post.id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 3
    assert all("content" in comment for comment in comments)


def test_get_non_existing_comment(client: TestClient):
    response = client.get("/comments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_update_comment_success(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    
    comment = client.post(
        "/comments/",
        json={"content": "Update me"},
        params={"post_id": test_post.id, "user_id": user1.id}
    ).json()
    
    comment_id = comment["id"]
    update_data = {"content": "Updated content"}
    
    response = client.put(
        f"/comments/{comment_id}",
        json=update_data,
        params={"user_id": user1.id}
    )
    
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"


def test_update_comment_unauthorized(client: TestClient, test_users: list, test_post: PostResponse):
    user1, user2 = test_users
    
    comment = client.post(
        "/comments/",
        json={"content": "My comment"},
        params={"post_id": test_post.id, "user_id": user1.id}
    ).json()
    
    response = client.put(
        f"/comments/{comment['id']}",
        json={"content": "Hacked!"},
        params={"user_id": user2.id}
    )
    
    assert response.status_code == 401
    assert "Not authorized" in response.json()["detail"]


def test_delete_comment_success(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    
    comment = client.post(
        "/comments/",
        json={"content": "Delete me"},
        params={"post_id": test_post.id, "user_id": user1.id}
    ).json()
    
    comment_id = comment["id"]
    response = client.delete(f"/comments/{comment_id}", params={"user_id": user1.id})
    
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]


def test_delete_comment_unauthorized(client: TestClient, test_users: list, test_post: PostResponse):
    user1, user2 = test_users
    
    comment = client.post(
        "/comments/",
        json={"content": "Protected"},
        params={"post_id": test_post.id, "user_id": user1.id}
    ).json()
    
    response = client.delete(f"/comments/{comment['id']}", params={"user_id": user2.id})
    assert response.status_code == 401