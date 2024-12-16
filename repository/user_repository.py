from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from utils.singleton_meta import SingletonMeta


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

    def update_user(self, user: User) -> Optional[User]:
        self.db.merge(user)
        self.db.commit()
        self.db.refresh(user)
        return user
      
    def delete_user(self, email: str) -> None:
        user = self.get_user_by_email(email)
        if user:
            self.db.delete(user)
            self.db.commit()
