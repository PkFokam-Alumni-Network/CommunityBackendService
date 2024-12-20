from typing import Optional, Type
from models.user import User
from repository.user_repository import UserRepository
from utils.func_utils import check_password, create_jwt
from utils.singleton_meta import SingletonMeta
from sqlalchemy.orm import Session
from fastapi import UploadFile
from werkzeug.utils import secure_filename
import os, shutil, hashlib

class UserService(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session=session)

    def login(self, email: str, password: str) -> str:
        user = self.user_repository.get_user_by_email(email)
        if not user or not check_password(password, user.password):
            raise ValueError("Invalid email or password")
        return create_jwt(user.email)

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
        if "mentor_email" in updated_data:
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
    
    def get_users(self) -> list[Type[User]]:
        return self.user_repository.get_users()

    def remove_user(self, email: str):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        return self.user_repository.delete_user(email)

    def generate_profile_picture_path(self, email:str, image: UploadFile ):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        max_file_size = 5 * 1024 * 1024
        allowed_types = ["image/jpeg", "image/png","image/jpg"]
        if image.content_type not in allowed_types:
            print(image.content_type)
            raise ValueError("Invalide file type. Only JPEG,JPG, PNG images are allowed")
        file_size = len(image.file.read())
        image.file.seek(0)
        if file_size > max_file_size:
            raise ValueError("File is too large. Maximum size allowed is 5MB.")
        hashed_email = hashlib.sha256(email.encode('utf-8')).hexdigest()
        Base_upload_dir = "uploads/profile_pictures"
        sanitized_file_name = secure_filename(image.filename)
        file_extension = sanitized_file_name.split('.')[-1]
        file_name = f"{hashed_email}.{file_extension}"
        file_path = os.path.join(Base_upload_dir, file_name)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            return file_path
        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            dir_path = os.path.dirname(file_path)
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
    
    def delete_profile_picture(self, email:str):
        user = self.user_repository.get_user_by_email(email)
        if user is None:
            raise ValueError("User does not exist.")
        if not user.image:
            raise ValueError("This user does not have a profile picture.")
        if not os.path.exists(user.image):
            raise ValueError("File not found.")
        os.remove(user.image)
        
        
        
        
        
        
         
        