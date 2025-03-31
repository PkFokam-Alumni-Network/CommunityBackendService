from datetime import datetime
from logging_config import LOGGER
from typing import List, Optional, Type

from sqlalchemy.orm import Session

from models.user import User
from repository.user_repository import UserRepository
from schemas import user_schema
from utils.func_utils import (check_password, create_jwt, get_password_hash, upload_image_to_s3)
from utils.image_utils import validate_image
from utils.singleton_meta import SingletonMeta


class UserService(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session=session)

    def login(self, email: str, password: str) -> user_schema.UserLoginResponse:
        user = self.user_repository.get_user_by_email(email)
        if not user or not check_password(password, user.password):
            raise ValueError("Invalid email or password")
        token = create_jwt(user.email)
        user_login_response: user_schema.UserLoginResponse = user_schema.UserLoginResponse.create_user_login_response(user, access_token=token)
        return user_login_response

    def register_user(self, email: str, first_name: str, last_name: str, password: str, **kwargs) -> User:
        user = self.user_repository.get_user_by_email(email)
        if user:
            raise ValueError("User with this email already exists.")
        mentor_email = kwargs.get('mentor_email')
        if mentor_email and mentor_email == email:
            raise ValueError("Mentor email cannot be the same as the user's email.")
        role = kwargs.get('role')
        if role and role not in ["user", "admin"]:
            raise ValueError(f"Role cannot be {role}. Defaut value is user")
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password,
            **kwargs
        )
        return self.user_repository.add_user(new_user)
    
    def update_user(self, email: str, updated_data: dict) -> Optional[User]:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found.")
        if "mentor_email" in updated_data and updated_data["mentor_email"]:
            mentor_email = updated_data["mentor_email"]
            mentor = self.user_repository.get_user_by_email(mentor_email)
            if not mentor:
                raise ValueError(f"Cannot assign mentor with email, {mentor_email} because user does not exist ")
            if mentor.email == email:
                raise ValueError("A mentor cannot be its own mentee!")
            user.mentor_email = mentor_email
        for key, value in updated_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return self.user_repository.update_user(user)

    def get_user_details(self, email: str) -> Optional[User]:
        return self.user_repository.get_user_by_email(email)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repository.get_user_by_id(user_id)
    
    def get_users(self) -> list[Type[User]]:
        return self.user_repository.get_users()

    def remove_user(self, email: str):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        return self.user_repository.delete_user(email)

    def save_profile_picture(self, email:str, image: str) -> str:
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        try:
            _ = validate_image(image)
            time = datetime.now().strftime('%Y-%m-%d')
            username, _ = email.split("@")
            file_name = f"profile-pictures/{time}/{username}.png"
            path = upload_image_to_s3(image, file_name)
            user.image = path
            self.user_repository.update_user(user)
            return path
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            LOGGER.error("Error saving profile picture. ", e)
            raise e
    
    def get_mentees(self, mentor_email: str) -> List[type[User]]:
        return self.user_repository.get_all_mentees(mentor_email)

    def unassign_mentor(self, mentee_email: str):
        mentee = self.user_repository.get_user_by_email(mentee_email)
        if not mentee.mentor_email:
            return 
        return self.update_user(mentee_email, {"mentor_email": None})

    def update_user_email(self, current_email: str, new_email: str) -> Optional[User]:
        user = self.user_repository.get_user_by_email(current_email)
        if not user:
            raise ValueError("User not found")
        user.email = new_email
        return self.user_repository.update_user(user)
    
    def update_password(self, old_password: str, new_password:str, email:str ) -> Optional[User]:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError("User not found")
        if not check_password(old_password, user.password):
            raise ValueError("Your old password does not match our records.")
        user.password = get_password_hash(new_password)
        return self.user_repository.update_user(user)
    

