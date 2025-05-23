from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, OperationalError
from models.user import User
from schemas.user_schema import UserCreate
from utils.singleton_meta import SingletonMeta
from utils.retry import retry_on_db_error

class UserRepository(metaclass=SingletonMeta):

    @retry_on_db_error()
    def add_user(self, db: Session, user: User) -> User:
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError(f"User with email {user.email} already exists.")
        except OperationalError as e:
            db.rollback()
            raise ConnectionError("Database connection error: " + str(e))
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")
    
    @retry_on_db_error()
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @retry_on_db_error()
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @retry_on_db_error()
    def get_users(self, db: Session, active) -> List[User]:
        if active:
            return db.query(User).filter(User.is_active == True).all()
        return db.query(User).all()

    @retry_on_db_error()
    def update_user(self, db: Session, user: User) -> Optional[User]:
        try:
            db.merge(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError(f"User with email {user.email} already exists.")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def delete_user(self, db: Session, user_id: int) -> None:
        user = self.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found.")
        
        try:
            db.delete(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Unable to delete user due to integrity constraints.")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while deleting the user: {e}")

    @retry_on_db_error()
    def get_all_mentees(self, db: Session, mentor_id: int) -> List[User]:
        user = self.get_user_by_id(db, mentor_id)
        if not user:
            raise ValueError("User not found.")
        try:
            mentees = db.query(User).filter(User.mentor_id == user.id).all()
            return mentees if mentees else []
        except Exception as e:
            raise RuntimeError(f"An error occurred while retrieving mentees: {e}")
