from typing import Optional
from models.user import User
from repository.user_repository import UserRepository
from utils.singleton_meta import SingletonMeta
from sqlalchemy.orm import Session


class UserService(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session=session)

    def register_user(self, email: str, first_name: str, last_name: str, password: str, **kwargs) -> User:
        user = self.user_repository.get_user_by_email(email)
        if user:
            raise ValueError("User with this email already exists.")
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **kwargs
        )
        return self.user_repository.add_user(new_user)
    
    def get_user_details(self, email: str) -> Optional[User]:
        return self.user_repository.get_user_by_email(email)

    def remove_user(self, email: str):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        self.user_repository.unassign_mentor(email)
        return self.user_repository.delete_user(email)
    
    def assign_mentor(self, mentor_email: str, mentee_email: str):
        mentor = self.user_repository.get_user_by_email(mentor_email)
        if mentor is None:
            raise ValueError("Cannot assign mentor with email", {mentor_email}, "because user does not exist !!!")
        mentee = self.user_repository.get_user_by_email(mentee_email)
        if mentee.mentor_email:
            raise ValueError("Mentee already has mentor !!!")
        if mentee is None:
            raise ValueError("User does not exist !!!")
        if mentor == mentee:
            raise ValueError("A mentor cannot be its own mentee !!!")
        return self.user_repository.assign_mentor(mentor_email, mentee_email)
        

    
    