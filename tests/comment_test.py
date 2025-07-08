import pytest
from typing import Generator
from fastapi.testclient import TestClient
from database import get_db
from models.comment import Comment
from models.post import Post
from models.user import User
from schemas.comment_schema import CommentResponse
from schemas.user_schema import UserCreatedResponse
from schemas.post_schema import PostResponse
from tests.conftest import create_and_teardown_tables, client

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db() -> Generator[TestClient, None, None]:
    yield from create_and_teardown_tables([User.metadata, Post.metadata, Comment.metadata])

@pytest.fixture(scope="function")
def test_users() -> list[User]:
    users = []
    for name in ["Alice", "Bob"]:
        response = client.post("/users/", json={
            "email": f"{name}@example.com",
            "first_name": name,
            "last_name": "Test",
            "password": "pass123"
        })
        user = UserCreatedResponse.model_validate(response.json())
        users.append(user)
    return users

@pytest.fixture(scope="function")
def test_post(test_users):
    user = test_users[0]
    response = client.post("/posts/", json={
        "title": "Test Post",
        "content": "Post content",
        "category": "General"
    }, params={"user_id": user.id})
    post = PostResponse.model_validate(response.json())
    return post

def test_create_get_comment(test_users, test_post):
    user = test_users[0]
    post = test_post

    comment_data = {"content": "Nice post!"}
    response = client.post(f"/posts/{post.id}/comments", json=comment_data, params={"user_id": user.id})
    
    assert response.status_code == 201
    new_comment: CommentResponse = CommentResponse.model_validate(response.json())
    assert new_comment.content == "Nice post!"
    assert new_comment.post_id == post.id
    assert new_comment.author_id == user.id

    response = client.get(f"/comments/{new_comment.id}")
    assert response.status_code == 200
    assert response.json()["content"] == "Nice post!"

def test_get_comments_by_post(test_users, test_post):
    user1, user2 = test_users[0], test_users[1]
    post = test_post

    # Add multiple comments
    for i in range(3):
        client.post(f"/posts/{post.id}/comments", json={"content": f"Comment {i} from {user1.first_name}"}, params={"user_id": user1.id})
        client.post(f"/posts/{post.id}/comments", json={"content": f"Comment {i} from {user2.first_name}"}, params={"user_id": user2.id})

    response = client.get(f"/posts/{post.id}/comments")
    assert response.status_code == 200
    assert len(response.json()) >= 6

def test_update_comment_success(test_users, test_post):
    user = test_users[0]
    post = test_post

    comment = client.post(f"/posts/{post.id}/comments", json={"content": "Old comment"}, params={"user_id": user.id})
    comment_id = comment.json()["id"]

    updated_comment = client.put(f"/comments/{comment_id}", json={"content": "Updated comment!"}, params={"user_id": user.id})
    assert updated_comment.status_code == 200
    assert updated_comment.json()["content"] == "Updated comment!"

def test_update_comment_unauthorized(test_users, test_post):
    owner, other_user = test_users[0], test_users[1]
    post = test_post

    comment = client.post(f"/posts/{post.id}/comments", json={"content": "Private comment"}, params={"user_id": owner.id})
    comment_id = comment.json()["id"]

    response = client.put(f"/comments/{comment_id}", json={"content": "Hacked"}, params={"user_id": other_user.id})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized."

def test_delete_comment_success(test_users, test_post):
    user = test_users[0]
    post = test_post

    comment = client.post(f"/posts/{post.id}/comments", json={"content": "To be deleted"}, params={"user_id": user.id}).json()

    response = client.delete(f"/comments/{comment['id']}", params={"user_id": user.id})
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]

def test_delete_comment_unauthorized(test_users, test_post):
    owner, other_user = test_users[0], test_users[1]
    post = test_post

    comment = client.post(f"/posts/{post.id}/comments", json={"content": "Stay away"}, params={"user_id": owner.id}).json()

    response = client.delete(f"/comments/{comment['id']}", params={"user_id": other_user.id})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized."

def test_get_non_existing_comment():
    response = client.get("/comments/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found."

def test_update_comment_empty_content(test_users, test_post):
    user = test_users[0]
    post = test_post

    comment = client.post(f"/posts/{post.id}/comments", json={"content": "Will go blank"}, params={"user_id": user.id}).json()

    response = client.put(f"/comments/{comment['id']}", json={"content": ""}, params={"user_id": user.id})
    assert response.status_code == 400
    assert response.json()["detail"] == "Content cannot be empty."
