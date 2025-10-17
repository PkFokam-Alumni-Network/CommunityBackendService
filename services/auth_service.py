from sqlalchemy.orm import Session
from core.logging_config import LOGGER
from repository.user_repository import UserRepository
from repository.session_repository import SessionRepository
from schemas import user_schema
from utils.func_utils import (
    check_password,
    create_jwt,
)

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.session_repo = SessionRepository()

    def verify_password(self, plain_password, hashed_password):
        return check_password(plain_password, hashed_password)

    def login(
        self, db: Session, email: str, password: str
    ) -> user_schema.UserLoginResponse:
        if not email or not password:
            raise ValueError("Email and password are required.")
        user = self.user_repo.get_user_by_email(db, email)
        if not user or not check_password(password, user.password):
            raise ValueError("Invalid email or password")
        token = create_jwt(user.email)
        user_login_response: user_schema.UserLoginResponse = (
            user_schema.UserLoginResponse.create_user_login_response(
                user, access_token=token
            )
        )
        self.session_repo.create_session(db, user.id, token)
        LOGGER.info(f"User {user.email} logged in successfully.")
        return user_login_response

    def logout(self, db: Session, token: str):
        self.session_repo.deactivate_session(db, token)
