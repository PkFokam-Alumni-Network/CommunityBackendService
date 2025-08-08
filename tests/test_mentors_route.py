from fastapi.testclient import TestClient
from schemas.user_schema import UserUpdateMentor, UserCreatedResponse
from pydantic import TypeAdapter
from typing import List


def setup_mentor_mentee(client: TestClient) -> int:
    """
    The function initializes a mentor and a mentee and add 
    their information into the test client db. Then, it 
    assigns the mentor to the mentee. Finally, the function 
    returns the updated_mentee data (in json) and the mentor_id

    :param client: an instance of TestClient.
    :type client: TestClient
    """

    mentee_data = {
        "email": "update_email_test@example.com",
        "first_name": "Email",
        "last_name": "Update",
        "password": "securepassword"
    }

    mentor_data = {
        "email": "test@example.com",
        "first_name": "test",
        "last_name": "Testing",
        "password": "securepassword"
    }

    first_response = client.post("/users/", json=mentee_data)
    second_response = client.post("/users", json=mentor_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    mentee = first_response.json()
    mentor = second_response.json()
    mentee_id = mentee['id']
    mentor_id = mentor['id']
    assign_route = f"/users/{mentor_id}/assign-mentor/{mentee_id}"
    response = client.put(assign_route)
    assert response.status_code == 200

    return (response.json(), mentor_id)


def test_assign_mentor(client: TestClient) -> None:
    """
    This function ensures that the assigned mentor is the one
    expected by comparing their ids

    :param client: an instance of the TestClient class
    :type client: TestClient
    """

    updated_mentee, mentor_id = setup_mentor_mentee(client)

    updated_user: UserUpdateMentor = UserUpdateMentor.model_validate(updated_mentee)
    assert updated_mentee["mentor_id"] == mentor_id

def test_unassign_mentor(client: TestClient) -> None:
    """
    This function validates the unassignement of a mentor 
    on a user.

    :param client: an instance of the TestClient class
    :type client: TestClient
    """

    updated_mentee, mentor_id = setup_mentor_mentee(client=client)
    
    unassign_route = f"/users/{updated_mentee["id"]}/unassign-mentor/"
    response = client.put(unassign_route)
    assert response.status_code == 200
    updated_user: UserUpdateMentor = UserUpdateMentor.model_validate(response.json())
    assert response.json()["mentor_id"] == None

def test_get_all_mentees(client: TestClient) -> None:
    """
    This function validates the number of students 
    that have been assigned to a mentor by comparing the
    length of the response with the number expected.

    :param client: an instance of the TestClient class
    :type client: TestClient
    """

    updated_mentee, mentor_id = setup_mentor_mentee(client=client)
    
    get_mentees_route = f"/users/{mentor_id}/mentees"
    response = client.get(get_mentees_route)
    assert response.status_code == 200
    users = TypeAdapter(List[UserCreatedResponse]).validate_python(response.json())
    assert isinstance(users, list)
    assert len(users) == 1