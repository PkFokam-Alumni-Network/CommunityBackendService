from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models.user import User
from utils.singleton_meta import SingletonMeta

class UserRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def add_user(self, user: User) -> User:
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {user.email} already exists.")
        except OperationalError as e:
            self.db.rollback()
            raise ConnectionError("Database connection error: " + str(e))
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_users(self) -> List[User]:
        return self.db.query(User).filter(User.is_active == True).all()    

    def update_user(self, user: User) -> Optional[User]:
        try:
            self.db.merge(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {user.email} already exists.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    def delete_user(self, email: str) -> None:
        user = self.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found.")
        
        try:
            self.db.delete(user)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Unable to delete user with email {email} due to integrity constraints.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred while deleting the user: {e}")

    def get_all_mentees(self, mentor_email: str) -> List[User]:
        try:
            mentees = self.db.query(User).filter(User.mentor_email == mentor_email).all()
            return mentees if mentees else []
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving mentees: {e}")
