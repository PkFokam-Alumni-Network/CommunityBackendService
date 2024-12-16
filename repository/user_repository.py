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


    def delete_user(self, email: str) -> None:
        user = self.get_user_by_email(email)
        if user:
            self.db.delete(user)
            self.db.commit()
    
    def assign_mentor(self, mentor_email: str, mentee_email: str) -> None:
        mentee = self.get_user_by_email(mentee_email)
        mentor = self.get_user_by_email(mentor_email)
        if mentee and mentor:
            mentee.mentor_email = mentor_email
            mentee.role = "mentee"  
            mentor.role = "mentor"  
            self.db.commit()
    
    def reinitialize_mentees_mentor(self, mentor_email: str) -> None:
        mentees = self.db.query(User).filter(User.mentor_email == mentor_email).all()
        for mentee in mentees:
            mentee.mentor_email = None
            mentee.role = "Null"
        self.db.commit()
