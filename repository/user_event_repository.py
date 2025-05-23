from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user_event import UserEvent
from models.user import User
from models.event import Event
from utils.singleton_meta import SingletonMeta

class UserEventRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def add_user_to_event(self, user_email: String, event_id: int) -> None:
        try:
            user = self.db.query(User).filter(User.email == user_email).first()
            if not user:
                raise ValueError(f"User with email {user_email} does not exist.")
            user_event = UserEvent(user_id=user.id, event_id=event_id)
            self.db.add(user_event)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {user_email} is already registered for event {event_id}.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred while adding user to event: {e}")

    def remove_user_from_event(self, user_email: String, event_id: int) -> None:
        try:
            user = self.db.query(User).filter(User.email == user_email).first()
            if not user:
                raise ValueError(f"User with email {user_email} does not exist.")
            user_event = self.db.query(UserEvent).filter_by(user_id=user.id, event_id=event_id).first()
            if user_event:
                self.db.delete(user_event)
                self.db.commit()
            else:
                raise ValueError(f"User with email {user_email} is not registered for event {event_id}.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred while removing user from event: {e}")

    def get_users_for_event(self, event_id: int) -> list[User]:
        return self.db.query(User).join(UserEvent).filter(UserEvent.event_id == event_id).all()

    def get_events_for_user(self, user_email: String) -> list[Event]:
        user = self.db.query(User).filter(User.email == user_email).first()
        if not user:
                raise ValueError(f"User with email {user_email} does not exist.")
        return self.db.query(Event).join(UserEvent).filter(UserEvent.user_id == user.id).all()

    def is_user_registered_for_event(self, user_email: String, event_id: int) -> bool:
        user = self.db.query(User).filter(User.email == user_email).first()
        if not user:
            raise ValueError(f"User with email {user_email} does not exist.")
        return self.db.query(UserEvent).filter(
            UserEvent.user_id == user.id,
            UserEvent.event_id == event_id
        ).count() > 0
    
    def delete_by_event_id(self, event_id: int):
        self.db.query(UserEvent).filter_by(event_id=event_id).delete()
        self.db.commit()
