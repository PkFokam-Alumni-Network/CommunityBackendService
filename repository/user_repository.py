from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models.user import User
from utils.singleton_meta import SingletonMeta
from utils.retry import retry_on_db_error

class UserRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    @retry_on_db_error()
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
    
    @retry_on_db_error()
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    @retry_on_db_error()
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    @retry_on_db_error()
    def get_users(self, active) -> List[User]:
        if active:
            return self.db.query(User).filter(User.is_active == True).all()
        return self.db.query(User).all()

    @retry_on_db_error()
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

    @retry_on_db_error()
    def delete_user(self, user_id: int) -> None:
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found.")
        
        try:
            self.db.delete(user)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Unable to delete user due to integrity constraints.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred while deleting the user: {e}")

    @retry_on_db_error()
    def get_all_mentees(self, mentor_id: int) -> List[User]:
        user = self.get_user_by_id(mentor_id)
        if not user:
            raise ValueError("User not found.")
        try:
            mentees = self.db.query(User).filter(User.mentor_id == user.id).all()
            return mentees if mentees else []
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving mentees: {e}")
