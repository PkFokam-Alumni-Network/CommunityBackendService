from typing import Optional
from models.user import User
from repository.user_repository import UserRepository
from utils.singleton_meta import SingletonMeta
from sqlalchemy.orm import Session
from fastapi import UploadFile
import os, shutil


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
    
    def update_user(self, email: str, updated_data: dict) -> Optional[User]:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found.")

        for key, value in updated_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return self.user_repository.update_user(user)

    def get_user_details(self, email: str) -> Optional[User]:
        return self.user_repository.get_user_by_email(email)
    
    def remove_user(self, email: str):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        return self.user_repository.delete_user(email)

    def generate_profile_picture_path(self, email:str, image: UploadFile ):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        file_path = f"uploads/profile_pictures/{email}/{image.filename}" 
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return file_path
    
    def delete_profile_picture(self, email:str):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        if not user.image:
            raise ValueError("This user does not have a profile picture.")
        if not os.path.exists(user.image):
            raise ValueError("File not found.")
        os.remove(user.image)
        
        
        
        
        
        
         
        