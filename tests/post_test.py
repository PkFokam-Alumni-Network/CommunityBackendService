import pytest
from fastapi.testclient import TestClient
from models.user import User
from schemas.post_schema import PostResponse
from schemas.user_schema import UserCreatedResponse
import base64
from models.enums import AttachmentType

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
    assert new_post.author.first_name == user1.first_name

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

def test_create_post_with_image_attachment(client, test_users, mocker):
    """Ensure posts with image attachments are uploaded correctly."""
    _, token1 = test_users[0]

    # Mock image validation and upload to S3
    mocker.patch("services.post_service.validate_image", return_value=True)
    mocker.patch("services.post_service.upload_image_to_s3", return_value="https://fake-s3-bucket.com/posts/test.png")

    fake_base64 = base64.b64encode(b"fake image bytes").decode("utf-8")

    post_data = {
        "title": "Post with Image",
        "content": "This post contains an image",
        "category": "Visuals",
        "attachment": fake_base64,
        "attachment_type": AttachmentType.IMAGE
    }

    response = client.post(
        "/posts/",
        json=post_data,
        cookies={"session_token": token1}
    )

    assert response.status_code == 201
    post = PostResponse.model_validate(response.json())
    assert post.attachment_type == AttachmentType.IMAGE
    assert post.attachment_url == "https://fake-s3-bucket.com/posts/test.png"


def test_create_post_with_link_attachment(client, test_users):
    """Allow link-based attachments (like Giphy or external URLs)."""
    _, token1 = test_users[0]

    post_data = {
        "title": "Post with GIF",
        "content": "Check this GIF out",
        "category": "Fun",
        "attachment": "https://giphy.com/some-funny-gif",
        "attachment_type": AttachmentType.GIPHY
    }

    response = client.post(
        "/posts/",
        json=post_data,
        cookies={"session_token": token1}
    )

    assert response.status_code == 201
    post = PostResponse.model_validate(response.json())
    assert post.attachment_type == AttachmentType.GIPHY
    assert post.attachment_url == "https://giphy.com/some-funny-gif"


def test_create_post_missing_attachment_error(client, test_users):
    """Attachment type provided but no attachment data -> validation error."""
    _, token1 = test_users[0]

    post_data = {
        "title": "Invalid Attachment Post",
        "content": "Missing attachment field",
        "category": "Testing",
        "attachment_type": AttachmentType.IMAGE
    }

    response = client.post(
        "/posts/",
        json=post_data,
        cookies={"session_token": token1}
    )

    assert response.status_code == 422  # Pydantic validation failure
    assert "attachment is required" in response.text


def test_update_post_with_new_attachment(client, test_users, mocker):
    """Allow updating a post to include a new image attachment."""
    _, token1 = test_users[0]

    # Create base post
    post = client.post(
        "/posts/",
        json={
            "title": "Update Test",
            "content": "Original content",
            "category": "Tech"
        },
        cookies={"session_token": token1}
    ).json()

    mocker.patch("services.post_service.validate_image", return_value=True)
    mocker.patch("services.post_service.upload_image_to_s3", return_value="https://fake-s3-bucket.com/posts/updated.png")

    new_base64 = base64.b64encode(b"new fake image bytes").decode("utf-8")

    update_data = {
        "title": "Updated Post with Image",
        "content": "Now has an attachment",
        "category": "Tech",
        "attachment": new_base64,
        "attachment_type": AttachmentType.IMAGE
    }

    response = client.put(
        f"/posts/{post['id']}",
        json=update_data,
        cookies={"session_token": token1}
    )

    assert response.status_code == 200
    post = PostResponse.model_validate(response.json())
    assert post.title == "Updated Post with Image"
    assert post.attachment_type == AttachmentType.IMAGE
    assert post.attachment_url == "https://fake-s3-bucket.com/posts/updated.png"

def test_post_response_includes_like_comment_counts(client: TestClient, test_users, test_post):
    _, token1 = test_users[0]

    resp = client.get(f"/posts/{test_post.id}", cookies={"session_token": token1})
    assert resp.status_code == 200
    data = resp.json()

    for key in ("likes_count", "comments_count", "liked_by_user"):
        assert key in data

    assert data["likes_count"] == 0
    assert data["comments_count"] == 0
    assert data["liked_by_user"] is False


def test_upvote_post_increments_like_count_and_sets_flag(client: TestClient, test_users, test_post):
    _, token1 = test_users[0]

    resp = client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})
    assert resp.status_code == 201

    upvote_data = resp.json()
    assert "likes_count" in upvote_data
    assert upvote_data["likes_count"] == 1

    post_resp = client.get(f"/posts/{test_post.id}", cookies={"session_token": token1})
    post_data = post_resp.json()
    assert post_data["likes_count"] == 1
    assert post_data["liked_by_user"] is True


def test_remove_upvote_decrements_like_count(client: TestClient, test_users, test_post):
    _, token1 = test_users[0]

    client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})

    resp = client.delete(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})
    assert resp.status_code == 200

    data = resp.json()
    assert "likes_count" in data
    assert data["likes_count"] == 0

    post_resp = client.get(f"/posts/{test_post.id}", cookies={"session_token": token1})
    assert post_resp.json()["liked_by_user"] is False


def test_multiple_users_upvote_counts_accumulate(client: TestClient, test_users, test_post):
    (_, token1), (_, token2) = test_users

    client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token1})
    client.post(f"/post/{test_post.id}/upvote", cookies={"session_token": token2})

    post_resp = client.get(f"/posts/{test_post.id}", cookies={"session_token": token1})
    post_data = post_resp.json()
    assert post_data["likes_count"] == 2
    assert post_data["liked_by_user"] is True


def test_comments_count_increments(client: TestClient, test_users, test_post):
    _, token1 = test_users[0]

    comment_data = {"content": "Nice post!"}
    resp = client.post(
        "/comments/",
        json=comment_data,
        params={"post_id": test_post.id},
        cookies={"session_token": token1},
    )
    assert resp.status_code == 201

    post_resp = client.get(f"/posts/{test_post.id}", cookies={"session_token": token1})
    assert post_resp.json()["comments_count"] == 1