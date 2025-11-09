import pytest
from fastapi.testclient import TestClient
from schemas.post_schema import PostResponse
from schemas.user_schema import UserCreatedResponse
from schemas.comment_schema import CommentResponse
import base64
from models.enums import AttachmentType

@pytest.fixture(scope="function")
def test_users(client: TestClient) -> list[tuple[UserCreatedResponse, str]]:
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
        "title": "Test Post for Comments",
        "content": "This post will have comments",
        "category": "Testing"
    }
    response = client.post("/posts/", json=post_data, cookies={"session_token": token1})
    assert response.status_code == 201
    return PostResponse.model_validate(response.json())


def test_create_comment(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    user1, token1 = test_users[0]
    comment_data = {
        "content": "This is my first comment"
    }

    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )
    assert response.status_code == 201
    comment = CommentResponse.model_validate(response.json())
    assert comment.content == "This is my first comment"
    assert comment.post_id == test_post.id
    assert comment.author.first_name == user1.first_name


def test_get_comment(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]
    comment_data = {"content": "Retrieve me"}

    created_comment = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    ).json()

    response = client.get(f"/comments/{created_comment['id']}")
    assert response.status_code == 200
    assert response.json()["content"] == "Retrieve me"


def test_get_comments_by_post(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]
    _, token2 = test_users[1]

    client.post("/comments/", json={"content": "First comment"}, params={"post_id": test_post.id}, cookies={"session_token": token1})
    client.post("/comments/", json={"content": "Second comment"}, params={"post_id": test_post.id}, cookies={"session_token": token2})
    client.post("/comments/", json={"content": "Third comment"}, params={"post_id": test_post.id}, cookies={"session_token": token1})

    response = client.get(f"/post/{test_post.id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 3
    assert all("content" in comment for comment in comments)


def test_get_non_existing_comment(client: TestClient):
    response = client.get("/comments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comment not found"


def test_update_comment_success(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]

    comment = client.post(
        "/comments/",
        json={"content": "Update me"},
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    ).json()

    comment_id = comment["id"]
    update_data = {"content": "Updated content"}

    response = client.put(
        f"/comments/{comment_id}",
        json=update_data,
        cookies={"session_token": token1}
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"


def test_update_comment_unauthorized(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    (_, token1), (_, token2) = test_users

    comment = client.post(
        "/comments/",
        json={"content": "My comment"},
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    ).json()

    response = client.put(
        f"/comments/{comment['id']}",
        json={"content": "Hacked!"},
        cookies={"session_token": token2}
    )

    assert response.status_code == 401
    assert "Not authorized" in response.json()["detail"]


def test_delete_comment_success(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    _, token1 = test_users[0]

    comment = client.post(
        "/comments/",
        json={"content": "Delete me"},
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    ).json()

    comment_id = comment["id"]
    response = client.delete(
        f"/comments/{comment_id}",
        cookies={"session_token": token1}
    )
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]


def test_delete_comment_unauthorized(client: TestClient, test_users: list[tuple[UserCreatedResponse, str]], test_post: PostResponse):
    (_, token1), (_, token2) = test_users

    comment = client.post(
        "/comments/",
        json={"content": "Protected"},
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    ).json()

    response = client.delete(
        f"/comments/{comment['id']}",
        cookies={"session_token": token2}
    )
    assert response.status_code == 401
    assert "Not authorized" in response.json()["detail"]

def test_create_comment_with_image_attachment(
    client,
    test_users,
    test_post,
    mocker
):
    """Ensure comments with image attachments are uploaded properly."""
    _, token1 = test_users[0]

    mocker.patch("services.comment_service.validate_image", return_value=True)
    mocker.patch("services.comment_service.upload_image_to_s3", return_value="https://fake-s3-bucket.com/comments/test.png")

    fake_base64 = base64.b64encode(b"fake image bytes").decode("utf-8")
    fake_image_data = f"data:image/png;base64,{fake_base64}"

    comment_data = {
        "content": "Here is an image",
        "attachment": fake_image_data,
        "attachment_type": AttachmentType.IMAGE
    }

    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )

    assert response.status_code == 201
    comment = CommentResponse.model_validate(response.json())
    assert comment.attachment_type == AttachmentType.IMAGE
    assert comment.attachment_url == "https://fake-s3-bucket.com/comments/test.png"


def test_create_comment_with_link_attachment(
    client,
    test_users,
    test_post
):
    """Allow Giphy or external links as non-image attachments."""
    _, token1 = test_users[0]

    comment_data = {
        "content": "Look at this GIF!",
        "attachment": "https://giphy.com/some-cool-gif",
        "attachment_type": AttachmentType.GIPHY
    }

    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )

    assert response.status_code == 201
    comment = CommentResponse.model_validate(response.json())
    assert comment.attachment_type == AttachmentType.GIPHY
    assert comment.attachment_url == "https://giphy.com/some-cool-gif"


def test_create_comment_missing_attachment_error(
    client,
    test_users,
    test_post
):
    """Attachment type provided but missing actual attachment -> validation error."""
    _, token1 = test_users[0]

    comment_data = {
        "content": "Missing attachment data",
        "attachment_type": AttachmentType.IMAGE
    }

    response = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )

    assert response.status_code == 422  # Pydantic validation error
    assert "attachment is required" in response.text

def test_update_comment_with_new_attachment(
    client,
    test_users,
    test_post,
    mocker
):
    """Update comment to add or replace an attachment."""
    _, token1 = test_users[0]

    # Create original comment
    created = client.post(
        "/comments/",
        json={"content": "Initial comment"},
        params={"post_id": test_post.id},
        cookies={"session_token": token1}
    )
    comment_id = created.json()["id"]

    mocker.patch("services.comment_service.validate_image", return_value=True)
    mocker.patch("services.comment_service.upload_image_to_s3", return_value="https://fake-s3-bucket.com/comments/updated.png")

    fake_base64 = base64.b64encode(b"new fake image").decode("utf-8")

    update_data = {
        "content": "Updated comment with attachment",
        "attachment": fake_base64,
        "attachment_type": AttachmentType.IMAGE
    }

    response = client.put(
        f"/comments/{comment_id}",
        json=update_data,
        cookies={"session_token": token1}
    )

    assert response.status_code == 200
    comment = CommentResponse.model_validate(response.json())
    assert comment.content == "Updated comment with attachment"
    assert comment.attachment_type == AttachmentType.IMAGE
    assert comment.attachment_url == "https://fake-s3-bucket.com/comments/updated.png"