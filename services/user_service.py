from datetime import datetime
from core.logging_config import LOGGER
from typing import List, Optional, Type

from sqlalchemy.orm import Session

from models.user import User
from repository.user_repository import UserRepository
from utils.func_utils import (
    check_password,
    get_password_hash,
    upload_image_to_s3,
)
from utils.image_utils import validate_image


class UserService():
    def __init__(self):
        self.user_repository = UserRepository()

    def register_user(
        self,
        db: Session,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
        **kwargs,
    ) -> User:
        if not all([email, first_name, last_name, password]):
            raise ValueError("Email, first name, last name, and password are required.")
        user = self.user_repository.get_user_by_email(db, email)
        if user:
            raise ValueError("User with this email already exists.")
        role = kwargs.get("role")
        if role and role not in ["user", "admin"]:
            raise ValueError(f"Role cannot be {role}. Defaut value is user")
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email.lower(),
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            **kwargs,
        )
        return self.user_repository.add_user(db, new_user)

    def update_user(
        self, db: Session, user_id: int, updated_data: dict
    ) -> Optional[User]:
        if not user_id:
            raise ValueError("User ID is required.")
        if not updated_data or not isinstance(updated_data, dict):
            raise ValueError("Updated data must be provided as a dictionary.")
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found.")
        for key, value in updated_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return self.user_repository.update_user(db, user)

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return self.user_repository.get_user_by_id(db, user_id)

    def get_users(self, db: Session, active: bool = False) -> list[Type[User]]:
        return self.user_repository.get_users(db, active=active)

    def remove_user(self, db: Session, user_id: int):
        user = self.user_repository.get_user_by_id(db, user_id)
        if user is None:
            raise ValueError("User does not exist.")
        return self.user_repository.delete_user(db, user_id)

    def save_profile_picture(self, db: Session, user_id: int, image: str) -> str:
        user = self.user_repository.get_user_by_id(db, user_id)
        if user is None:
            raise ValueError("User does not exist.")
        try:
            email: str = user.email
            _ = validate_image(image)
            time = datetime.now().strftime("%Y-%m-%d")
            username, _ = email.split("@")
            file_name = f"profile-pictures/{time}/{username}.png"
            path = upload_image_to_s3(image, file_name)
            user.image = path
            self.user_repository.update_user(db, user)
            return path
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            LOGGER.error("Error saving profile picture. ", e)
            raise e

    def get_mentees(self, db: Session, user_id: int) -> List[type[User]]:
        return self.user_repository.get_all_mentees(db, user_id)

    # TODO: Uncomment and implement this method when the mentor assignment feature with id is implemented
    def unassign_mentor(self, db: Session, mentee_email: str):
        mentee = self.user_repository.get_user_by_email(db, mentee_email)
        if not mentee.mentor_id:
            return
        return self.update_user(db, mentee_email, {"mentor_email": None})

    def update_user_email(
        self, db: Session, user_id: int, new_email: str
    ) -> Optional[User]:
        if not user_id:
            raise ValueError("User ID is required.")
        if not new_email:
            raise ValueError("New email is required.")
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        user.email = new_email
        return self.user_repository.update_user(db, user)

    def update_password(
        self, db: Session, old_password: str, new_password: str, user_id: int
    ) -> Optional[User]:
        if not user_id:
            raise ValueError("User ID is required.")
        if not old_password or not new_password:
            raise ValueError("Old password and new password are required.")
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        if not check_password(old_password, user.password):
            raise ValueError("Your old password does not match our records.")
        user.password = get_password_hash(new_password)
        return self.user_repository.update_user(db, user)
    
    def reset_password(self, db: Session, user_id: int, new_password: str) -> Optional[User]:
        if not user_id:
            raise ValueError("User ID is required.")
        if not new_password:
            raise ValueError("New password is required.")
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        user.password = get_password_hash(new_password)
        return self.user_repository.update_user(db, user)
    
    def get_users_by_ids(self, db: Session, user_ids: List[int]) -> List[User]:
        if not user_ids:
            raise ValueError("User IDs list cannot be empty.")
        return self.user_repository.get_users_by_ids(db, user_ids)

    def get_users_by_emails(self, db: Session, emails: List[str]) -> List[User]:
        if not emails:
            raise ValueError("Emails list cannot be empty.")
        return self.user_repository.get_users_by_emails(db, emails)
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return self.user_repository.get_user_by_email(db, email)


