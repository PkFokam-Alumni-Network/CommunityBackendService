from typing import Generator
from fastapi.testclient import TestClient
import pytest
from models.announcement import Announcement
from tests.conftest import create_and_teardown_tables, client

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db() -> Generator[TestClient, None, None]:
    yield from create_and_teardown_tables(Announcement.metadata)

def test_create_get_announcement() -> None:
    create_route = "/announcements/"
    response = client.post(
        create_route,
        json={
            "title": "Test Announcement",
            "description": "This is a test announcement.",
            "announcement_date": "2023-10-10T10:00:00",
            "announcement_deadline": "2023-12-31T23:59:59",
            "image": "test_image_url"
        },
    )

    assert response.status_code == 201
    announcement_id: int = response.json()["id"]
    get_route = f"/announcements/{announcement_id}"
    response = client.get(get_route)
    assert response.status_code == 200
    assert response.json()["id"] == announcement_id
    assert response.json()["title"] == "Test Announcement"

def test_get_non_existing_announcement() -> None:
    response = client.get("/announcements/999")
    assert response.status_code == 404

def test_create_announcement_duplicate() -> None:
    response = client.post(
        "/announcements/",
        json={
            "title": "Duplicate Announcement",
            "description": "This is a duplicate announcement.",
            "announcement_date": "2023-10-10T10:00:00",
            "announcement_deadline": "2023-12-31T23:59:59",
            "image": "duplicate_image_url"
        },
    )
    assert response.status_code == 201
    response = client.post(
        "/announcements/",
        json={
            "title": "Duplicate Announcement",
            "description": "This is a duplicate announcement.",
            "announcement_date": "2023-10-10T10:00:00",
            "announcement_deadline": "2023-12-31T23:59:59",
            "image": "duplicate_image_url"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Announcement with this title already exists."

def test_create_announcement_date_before_deadline() -> None:
    response = client.post(
        "/announcements/",
        json={
            "title": "Date Before Deadline",
            "description": "This announcement has a date before the deadline.",
            "announcement_date": "2023-12-31T10:00:00",
            "announcement_deadline": "2023-12-31T09:59:59",
            "image": "date_before_deadline_image_url"
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Announcement date must be before announcement deadline."


def test_delete_existing_announcement() -> None:
    create_response = client.post(
        "/announcements/",
        json={
            "title": "Delete Announcement",
            "description": "This announcement will be deleted.",
            "announcement_date": "2023-10-10T10:00:00",
            "announcement_deadline": "2023-12-31T23:59:59",
            "image": "delete_image_url"
        },
    )
    assert create_response.status_code == 201
    new_announcement = create_response.json()
    announcement_id = new_announcement["id"]
    delete_route = f"/announcements/{announcement_id}"
    delete_response = client.delete(delete_route)
    assert delete_response.status_code == 200
    assert delete_response.json()["id"] == announcement_id
    assert delete_response.json()["message"] == "Announcement deleted successfully."
    delete_response = client.delete(delete_route)
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Announcement not found"
