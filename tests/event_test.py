from fastapi.testclient import TestClient
from schemas.event_schema import EventCreate, EventResponse
from schemas.user_schema import UserCreatedResponse
from pydantic import TypeAdapter
from typing import List
from datetime import datetime, timedelta, timezone


def test_create_event(client: TestClient) -> None:
    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    event_data = {
        "title": "Test Event",
        "start_time": future_time.isoformat(),
        "end_time": (future_time + timedelta(hours=6)).isoformat(),
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    response = client.post("/events/", json=event_data)
    assert response.status_code == 201
    event_created_response: EventCreate = EventCreate.model_validate(response.json())
    assert event_created_response.title == "Test Event"
    assert event_created_response.location == "Event Location"
    assert event_created_response.is_active


def test_get_event_by_id(client: TestClient) -> None:
    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    event_data = {
        "title": "Test Event",
        "start_time": future_time.isoformat(),
        "end_time": (future_time + timedelta(hours=6)).isoformat(),
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    response = client.post("/events/", json=event_data)
    event: EventResponse = EventResponse.model_validate(response.json())
    event_id = event.id
    get_response = client.get(f"/events/{event_id}")
    assert get_response.status_code == 200
    fetched_event = EventResponse.model_validate(get_response.json())
    assert fetched_event.title == "Test Event"
    assert fetched_event.location == "Event Location"


def test_add_user_to_event(client: TestClient) -> None:
    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    event_data = {
        "title": "Test Event",
        "start_time": future_time.isoformat(),
        "end_time": (future_time + timedelta(hours=6)).isoformat(),
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    event_response = client.post("/events/", json=event_data)
    assert event_response.status_code == 201

    event: EventResponse = EventResponse.model_validate(event_response.json())
    user_data = {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "testpassword",
    }
    user_response = client.post("/users/", json=user_data)
    _: UserCreatedResponse = UserCreatedResponse.model_validate(user_response.json())

    add_user_response = client.post(
        f"/events/{event.id}/register", json={"email": "user@example.com"}
    )
    assert add_user_response.status_code == 200


def test_remove_user_from_event(client: TestClient) -> None:
    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    event_data = {
        "title": "Test Event",
        "start_time": future_time.isoformat(),
        "end_time": (future_time + timedelta(hours=6)).isoformat(),
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
        "password": "testpassword",
    }
    client.post("/users/", json=user_data)

    add_user_response = client.post(
        f"/events/{event['id']}/register", json={"email": "user@example.com"}
    )
    assert add_user_response.status_code == 200

    remove_user_response = client.post(
        f"/events/{event['id']}/unregister", json={"email": "user@example.com"}
    )
    assert remove_user_response.status_code == 200


def test_get_all_event_attendees(client: TestClient) -> None:
    future_time = datetime.now(timezone.utc) + timedelta(days=7)
    event_data = {
        "title": "Test Event",
        "start_time": future_time.isoformat(),
        "end_time": (future_time + timedelta(hours=6)).isoformat(),
        "location": "Event Location",
        "description": "This is a test event",
        "categories": "Tech, Development",
    }
    event_response = client.post("/events/", json=event_data)
    event: EventResponse = EventResponse.model_validate(event_response.json())

    user_data = {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "testpassword",
    }
    user_response = client.post("/users/", json=user_data)
    user: UserCreatedResponse = UserCreatedResponse.model_validate(user_response.json())

    add_user_response = client.post(
        f"/events/{event.id}/register", json={"email": "user@example.com"}
    )
    assert add_user_response.status_code == 200

    response = client.get(f"/events/{event.id}/users")
    assert response.status_code == 200

    attendees = TypeAdapter(List[UserCreatedResponse]).validate_python(response.json())
    assert len(attendees) == 1
    assert attendees[0].email == user.email


def test_cannot_register_for_past_event(client: TestClient) -> None:
    past_time = datetime.now(timezone.utc) - timedelta(days=1)
    event_data = {
        "title": "Past Event",
        "start_time": (past_time - timedelta(hours=2)).isoformat(),
        "end_time": past_time.isoformat(),
        "location": "Test Location",
        "description": "This event has already ended",
        "categories": "Test",
    }

    event_response = client.post("/events/", json=event_data)
    assert event_response.status_code == 201
    event: EventResponse = EventResponse.model_validate(event_response.json())

    user_data = {
        "email": "pastuser@example.com",
        "first_name": "Past",
        "last_name": "User",
        "password": "testpassword",
    }
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 201

    registration_response = client.post(
        f"/events/{event.id}/register", json={"email": "pastuser@example.com"}
    )

    assert registration_response.status_code == 400
    assert "Cannot register for past events" in registration_response.json()["detail"]
