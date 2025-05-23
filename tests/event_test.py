from fastapi.testclient import TestClient
from schemas.event_schema import EventResponse
from schemas.user_schema import UserCreatedResponse

def test_create_event(client: TestClient) -> None:
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

def test_get_event_by_id(client: TestClient) -> None:
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

def test_add_user_to_event(client: TestClient) -> None:
    event_data = {
        "title": "Test Event",
        "start_time": "2025-01-24T11:30",
        "end_time": "2025-01-24T17:30",
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
        "password": "testpassword"
    }
    user_response = client.post("/users/", json=user_data)
    user: UserCreatedResponse = UserCreatedResponse.model_validate(user_response.json())

    add_user_response = client.post(f"/events/{event.id}/register", json={'email':'user@example.com'})
    assert add_user_response.status_code == 200

def test_remove_user_from_event(client: TestClient) -> None:
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
    client.post("/users/", json=user_data)

    add_user_response = client.post(f"/events/{event['id']}/register", json={'email':'user@example.com'})
    assert add_user_response.status_code == 200

    remove_user_response = client.post(f"/events/{event['id']}/unregister", json={'email':'user@example.com'})
    assert remove_user_response.status_code == 200

def test_get_all_event_attendees(client: TestClient) -> None:
    event_data = {
        "title": "Test Event",
        "start_time": "2025-01-24T11:30",
        "end_time": "2025-01-24T17:30",
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
        "password": "testpassword"
    }
    user_response = client.post("/users/", json=user_data)
    user: UserCreatedResponse = UserCreatedResponse.model_validate(user_response.json())

    add_user_response = client.post(f"/events/{event.id}/register", json={'email':'user@example.com'})
    assert add_user_response.status_code == 200

    response = client.get(f"/events/{event.id}/users")
    assert response.status_code == 200
    attendees = response.json()
    assert len(attendees) == 1
    assert attendees[0]["email"] ==user.email