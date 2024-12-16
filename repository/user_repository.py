from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from utils.singleton_meta import SingletonMeta
import boto3
import uuid
from fastapi import UploadFile
from botocore.exceptions import NoCredentialsError
import os0

class UserRepository(metaclass=SingletonMeta):
    def __init__(self, session):
        self.db: Session = session

    def add_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()


    def delete_user(self, email: str) -> None:
        user = self.get_user_by_email(email)
        if user:
            self.db.delete(user)
            self.db.commit()
    
    def store_profile_picture(self, ) -> image_path:
        
    
    def update_profile_picture(self, email: str, pp_url: str) -> None:
        user = self.get_user_by_email(email)
        if user:
            user.image = pp_url
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete_profile_picture(self, email: str) -> None:
        user = self.get_user_by_email(email)
        if user and user.image:
            user.image = None
            self.db.commit()
            self.db.refresh(user)
        return user
        