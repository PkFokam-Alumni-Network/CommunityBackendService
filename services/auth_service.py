from sqlalchemy.orm import Session
from core.logging_config import LOGGER
from typing import Optional
from models.user import User
from repository.user_repository import UserRepository
from repository.session_repository import SessionRepository
from passlib.context import CryptContext
from schemas import user_schema
from utils.func_utils import (
    check_password,
    create_jwt,
    reset_password_email,
    verify_jwt,
    get_password_hash,
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.session_repo = SessionRepository()

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

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
        self.session_repo.create_session(db, user.id)
        return user_login_response

    def logout(self, db: Session, token: str):
        self.session_repo.deactivate_session(db, token)

    def request_password_reset(self, db: Session, email: str) -> Optional[User]:
        if not email:
            raise ValueError("Email is required.")
        user = self.user_repo.get_user_by_email(db, email)
        user_name = user.first_name if user else None
        if not user:
            raise ValueError("User not found")
        try:
            token = create_jwt(email)
            reset_password_email(email, token, user_name)
        except Exception as e:
            LOGGER.error("Error sending reset password email. ", e)
            raise e

    def reset_password(
        self, db: Session, new_password: str, token: str
    ) -> Optional[User]:
        if not new_password or not token:
            raise ValueError("New password and token are required.")
        try:
            decoded_token = verify_jwt(token)
            email = decoded_token["user_id"]
            user = self.user_repo.get_user_by_email(db, email)
            if not user:
                raise ValueError("User not found")
            user.password = get_password_hash(new_password)
            return self.user_repo.update_user(db, user)
        except Exception as e:
            LOGGER.error("Error resetting password. ", e)
            raise e
