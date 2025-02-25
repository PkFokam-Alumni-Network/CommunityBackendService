from typing import Generator
import pytest
from fastapi.testclient import TestClient
from models.event import Event
from models.user import User
from models.user_event import UserEvent
from tests.conftest import create_and_teardown_tables, client

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db() -> Generator[TestClient, None, None]:
    yield from create_and_teardown_tables([Event.metadata, User.metadata, UserEvent.metadata])


def test_create_event() -> None:
    event_data = {
        "title": "Test Event",
        "start_time": "2025-01-24T11:30",
        "end_time": "2025-01-24T17:30",
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    response = client.post("/events/", json=event_data)
    assert response.status_code == 201
    event = response.json()
    assert event["title"] == "Test Event"
    assert event["location"] == "Event Location"

def test_get_event_by_id() -> None:
    event_data = {
        "title": "Test Event",
        "start_time": "2025-01-24T11:30",
        "end_time": "2025-01-24T17:30",
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    response = client.post("/events/", json=event_data)
    event = response.json()
    event_id = event["id"]
    response = client.get(f"/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Event"
    assert response.json()["location"] == "Event Location"

def test_add_user_to_event() -> None:
    event_data = {
        "title": "Test Event",
        "start_time": "2025-01-24T11:30",
        "end_time": "2025-01-24T17:30",
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    event_response = client.post("/events/", json=event_data)
    event = event_response.json()

    user_data = {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "testpassword"
    }
    user_response = client.post("/users/", json=user_data)
    user = user_response.json()

    add_user_response = client.post(f"/events/{event['id']}/register/{user['id']}")
    assert add_user_response.status_code == 200
    assert add_user_response.json()["message"] == f"User {user['email']} added to event."

def test_remove_user_from_event() -> None:
    event_data = {
        "title": "Test Event",
        "start_time": "2025-01-24T11:30",
        "end_time": "2025-01-24T17:30",
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    event_response = client.post("/events/", json=event_data)
    event = event_response.json()

    user_data = {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "testpassword"
    }
    user_response = client.post("/users/", json=user_data)
    user = user_response.json()

    add_user_response = client.post(f"/events/{event['id']}/register/{user['id']}")
    assert add_user_response.status_code == 200

    remove_user_response = client.post(f"/events/{event['id']}/unregister/{user['id']}")
    assert remove_user_response.status_code == 200
    assert remove_user_response.json()["message"] == f"User {user['email']} removed from event."

