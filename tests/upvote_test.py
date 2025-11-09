import pytest
from fastapi.testclient import TestClient
from schemas.post_schema import PostResponse
from schemas.user_schema import UserCreatedResponse
from schemas.comment_schema import CommentResponse

@pytest.fixture(scope="function")
def test_users(client: TestClient) -> list[tuple[UserCreatedResponse, str]]:
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
        "email": user1_data["email"],
        "password": user1_data["password"]
    })
    login2_response = client.post("/login", json={
        "email": user2_data["email"],
        "password": user2_data["password"]
    })

    token1 = login1_response.cookies.get("session_token")
    token2 = login2_response.cookies.get("session_token")

    return [(user1, token1), (user2, token2)]


@pytest.fixture(scope="function")
def test_post(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]]) -> PostResponse:
    _, token1 = test_users[0]
    post_data = {
        "title": "Test Post for Upvotes",
        "content": "This post will have upvotes",
        "category": "Testing"
    }
    response = client.post("/posts/", json=post_data, cookies={"session_token": token1})
    assert response.status_code == 201
    return PostResponse.model_validate(response.json())


@pytest.fixture(scope="function")
def test_comment(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse) -> CommentResponse:
    _, token1 = test_users[0]
    comment_data = {"content": "Test comment for upvotes"}
    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )
    assert response.status_code == 201
    return CommentResponse.model_validate(response.json())


def test_upvote_post_success(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    user1, token1 = test_users[0]

    response = client.post(
        f"/post/{test_post.id}/upvote",
        cookies={"session_token": token1}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Post upvoted successfully"
    assert data["upvote"]["post_id"] == test_post.id
    assert data["upvote"]["user_id"] == user1.id
    assert data["upvote"]["comment_id"] is None


def test_upvote_post_duplicate(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]

    # First upvote
    client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})

    # Second upvote (should fail)
    response = client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})

    assert response.status_code == 400
    assert "already upvoted" in response.json()["detail"]


def test_remove_upvote_from_post_success(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]

    # First upvote the post
    client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})

    # Remove upvote
    response = client.delete(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})

    assert response.status_code == 200
    assert response.json()["message"] == "Upvote removed successfully"


def test_remove_upvote_from_post_not_found(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]

    # Try to remove upvote that doesn't exist
    response = client.delete(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})

    assert response.status_code == 404
    assert "Upvote not found" in response.json()["detail"]


def test_upvote_comment_success(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_comment: CommentResponse):
    user2, token2 = test_users[1]

    response = client.post(
        f"/comment/{test_comment.id}/upvote",
        cookies={"session_token": token2}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Comment upvoted successfully"
    assert data["upvote"]["comment_id"] == test_comment.id
    assert data["upvote"]["user_id"] == user2.id
    assert data["upvote"]["post_id"] is None


def test_upvote_comment_duplicate(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_comment: CommentResponse):
    _, token1 = test_users[0]

    # First upvote
    client.post(f"/comment/{test_comment.id}/upvote", cookies={"session_token": token1})

    # Second upvote (should fail)
    response = client.post(f"/comment/{test_comment.id}/upvote", cookies={"session_token": token1})

    assert response.status_code == 400
    assert "already upvoted" in response.json()["detail"]


def test_remove_upvote_from_comment_success(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_comment: CommentResponse):
    _, token1 = test_users[0]

    # First upvote the comment
    client.post(f"/comment/{test_comment.id}/upvote", cookies={"session_token": token1})

    # Remove upvote
    response = client.delete(f"/comment/{test_comment.id}/upvote", cookies={"session_token": token1})

    assert response.status_code == 200
    assert response.json()["message"] == "Upvote removed successfully"


def test_remove_upvote_from_comment_not_found(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_comment: CommentResponse):
    _, token2 = test_users[1]

    # Try to remove upvote that doesn't exist
    response = client.delete(f"/comment/{test_comment.id}/upvote", cookies={"session_token": token2})

    assert response.status_code == 404
    assert "Upvote not found" in response.json()["detail"]


def test_multiple_users_upvote_same_post(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    (_, token1), (_, token2) = test_users

    # Both users upvote the same post
    response1 = client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})
    response2 = client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token2})

    assert response1.status_code == 201
    assert response2.status_code == 201


def test_user_can_upvote_multiple_posts(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]]):
    _, token1 = test_users[0]

    # Create two posts
    post1_resp = client.post("/posts/", json={
        "title": "Post 1",
        "content": "Content 1",
        "category": "Test"
    }, cookies={"session_token": token1})
    post2_resp = client.post("/posts/", json={
        "title": "Post 2",
        "content": "Content 2",
        "category": "Test"
    }, cookies={"session_token": token1})

    assert post1_resp.status_code == 201
    assert post2_resp.status_code == 201

    post1 = post1_resp.json()
    post2 = post2_resp.json()

    # User upvotes both posts
    response1 = client.post(f"/post/{post1['id']}/upvote", cookies={"session_token": token1})
    response2 = client.post(f"/post/{post2['id']}/upvote", cookies={"session_token": token1})

    assert response1.status_code == 201
    assert response2.status_code == 201


def test_comment_includes_upvote_count(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    (_, token1), (_, token2) = test_users

    # Create a comment
    comment_resp = client.post(
        "/comments/",
        json={"content": "Test comment"},
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )
    assert comment_resp.status_code == 201
    comment = comment_resp.json()

    # Two users upvote the comment
    client.post(f"/comment/{comment['id']}/upvote", cookies={"session_token": token1})
    client.post(f"/comment/{comment['id']}/upvote", cookies={"session_token": token2})

    # Get comments for the post
    response = client.get(f"/post/{test_post.id}/comments", cookies={"session_token": token1})
    comments = response.json()

    assert response.status_code == 200
    assert len(comments) == 1
    assert comments[0]["upvote_count"] == 2