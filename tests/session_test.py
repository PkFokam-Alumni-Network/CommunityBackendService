from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from core.database import get_db
from models.session import Session as SessionModel

def _create_user_and_login(client: TestClient, email="session_test@example.com"):
    user_data = {
        "email": email,
        "first_name": "Session",
        "last_name": "Tester",
        "password": "securepassword",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201

    response = client.post("/login/", json={"email": email, "password": "securepassword"})
    assert response.status_code == 200
    cookies = response.cookies
    assert "session_token" in cookies
    return cookies.get("session_token"), email

def test_session_created_on_login(client: TestClient):
    token, _ = _create_user_and_login(client)

    db: Session = next(get_db())
    session = db.query(SessionModel).filter(SessionModel.session_token == token).first()
    assert session is not None
    assert session.user_id is not None
    assert session.expires_at > datetime.now(timezone.utc)
    db.close()

def test_expired_session_rejected(client: TestClient):
    token, _ = _create_user_and_login(client)

    db: Session = next(get_db())
    session = db.query(SessionModel).filter(SessionModel.session_token == token).first()
    session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    db.close()

    response = client.get("/users/", cookies={"session_token": token})
    assert response.status_code == 401
    assert response.json()["detail"].lower() == "session expired"

def test_cleanup_expired_sessions(client: TestClient):
    token, _ = _create_user_and_login(client)

    db: Session = next(get_db())
    session = db.query(SessionModel).filter(SessionModel.session_token == token).first()
    session.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db.commit()


    deleted = db.query(SessionModel).filter(SessionModel.session_token == token).first()
    assert deleted is None
    db.close()
