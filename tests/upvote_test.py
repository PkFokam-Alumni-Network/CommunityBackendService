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
        "title": "Test Post for Upvotes",
        "content": "This post will have upvotes",
        "category": "Testing"
    }
    response = client.post("/posts/", json=post_data, params={"user_id": user1.id})
    return PostResponse.model_validate(response.json())


@pytest.fixture(scope="function")
def test_comment(client: TestClient, test_users: list, test_post: PostResponse) -> CommentResponse:
    user1 = test_users[0]
    comment_data = {"content": "Test comment for upvotes"}
    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id, "user_id": user1.id}
    )
    return CommentResponse.model_validate(response.json())


def test_upvote_post_success(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    
    response = client.post(
        f"/upvotes/post/{test_post.id}",
        params={"user_id": user1.id}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Post upvoted successfully"
    assert data["upvote"]["post_id"] == test_post.id
    assert data["upvote"]["user_id"] == user1.id
    assert data["upvote"]["comment_id"] is None


def test_upvote_post_duplicate(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    
    # First upvote
    client.post(f"/upvotes/post/{test_post.id}", params={"user_id": user1.id})
    
    # Second upvote (should fail)
    response = client.post(f"/upvotes/post/{test_post.id}", params={"user_id": user1.id})
    
    assert response.status_code == 400
    assert "already upvoted" in response.json()["detail"]


def test_remove_upvote_from_post_success(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    
    # First upvote the post
    client.post(f"/upvotes/post/{test_post.id}", params={"user_id": user1.id})
    
    # Remove upvote
    response = client.delete(f"/upvotes/post/{test_post.id}", params={"user_id": user1.id})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Upvote removed successfully"


def test_remove_upvote_from_post_not_found(client: TestClient, test_users: list, test_post: PostResponse):
    user1 = test_users[0]
    
    # Try to remove upvote that doesn't exist
    response = client.delete(f"/upvotes/post/{test_post.id}", params={"user_id": user1.id})
    
    assert response.status_code == 404
    assert "Upvote not found" in response.json()["detail"]


def test_upvote_comment_success(client: TestClient, test_users: list, test_comment: CommentResponse):
    user2 = test_users[1]
    
    response = client.post(
        f"/upvotes/comment/{test_comment.id}",
        params={"user_id": user2.id}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Comment upvoted successfully"
    assert data["upvote"]["comment_id"] == test_comment.id
    assert data["upvote"]["user_id"] == user2.id
    assert data["upvote"]["post_id"] is None


def test_upvote_comment_duplicate(client: TestClient, test_users: list, test_comment: CommentResponse):
    user1 = test_users[0]
    
    # First upvote
    client.post(f"/upvotes/comment/{test_comment.id}", params={"user_id": user1.id})
    
    # Second upvote (should fail)
    response = client.post(f"/upvotes/comment/{test_comment.id}", params={"user_id": user1.id})
    
    assert response.status_code == 400
    assert "already upvoted" in response.json()["detail"]


def test_remove_upvote_from_comment_success(client: TestClient, test_users: list, test_comment: CommentResponse):
    user1 = test_users[0]
    
    # First upvote the comment
    client.post(f"/upvotes/comment/{test_comment.id}", params={"user_id": user1.id})
    
    # Remove upvote
    response = client.delete(f"/upvotes/comment/{test_comment.id}", params={"user_id": user1.id})
    
    assert response.status_code == 200
    assert response.json()["message"] == "Upvote removed successfully"


def test_remove_upvote_from_comment_not_found(client: TestClient, test_users: list, test_comment: CommentResponse):
    user2 = test_users[1]
    
    # Try to remove upvote that doesn't exist
    response = client.delete(f"/upvotes/comment/{test_comment.id}", params={"user_id": user2.id})
    
    assert response.status_code == 404
    assert "Upvote not found" in response.json()["detail"]


def test_multiple_users_upvote_same_post(client: TestClient, test_users: list, test_post: PostResponse):
    user1, user2 = test_users
    
    # Both users upvote the same post
    response1 = client.post(f"/upvotes/post/{test_post.id}", params={"user_id": user1.id})
    response2 = client.post(f"/upvotes/post/{test_post.id}", params={"user_id": user2.id})
    
    assert response1.status_code == 201
    assert response2.status_code == 201


def test_user_can_upvote_multiple_posts(client: TestClient, test_users: list):
    user1 = test_users[0]
    
    # Create two posts
    post1 = client.post("/posts/", json={
        "title": "Post 1",
        "content": "Content 1",
        "category": "Test"
    }, params={"user_id": user1.id}).json()
    
    post2 = client.post("/posts/", json={
        "title": "Post 2",
        "content": "Content 2",
        "category": "Test"
    }, params={"user_id": user1.id}).json()
    
    # User upvotes both posts
    response1 = client.post(f"/upvotes/post/{post1['id']}", params={"user_id": user1.id})
    response2 = client.post(f"/upvotes/post/{post2['id']}", params={"user_id": user1.id})
    
    assert response1.status_code == 201
    assert response2.status_code == 201


def test_comment_includes_upvote_count(client: TestClient, test_users: list, test_post: PostResponse):
    user1, user2 = test_users
    
    # Create a comment
    comment = client.post(
        "/comments/",
        json={"content": "Test comment"},
        params={"post_id": test_post.id, "user_id": user1.id}
    ).json()
    
    # Two users upvote the comment
    client.post(f"/upvotes/comment/{comment['id']}", params={"user_id": user1.id})
    client.post(f"/upvotes/comment/{comment['id']}", params={"user_id": user2.id})
    
    # Get comments for the post
    response = client.get(f"/comments/post/{test_post.id}")
    comments = response.json()
    
    assert response.status_code == 200
    assert len(comments) == 1
    assert comments[0]["upvote_count"] == 2