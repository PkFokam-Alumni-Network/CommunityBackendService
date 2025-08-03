from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user_event import UserEvent
from models.user import User
from models.event import Event
from utils.singleton_meta import SingletonMeta
from utils.retry import retry_on_db_error


class UserEventRepository(metaclass=SingletonMeta):
    @retry_on_db_error()
    def add_user_to_event(self, db: Session, user_email: String, event_id: int) -> None:
        try:
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                raise ValueError(f"User with email {user_email} does not exist.")
            user_event = UserEvent(user_id=user.id, event_id=event_id)
            db.add(user_event)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(
                f"User with email {user_email} is already registered for event {event_id}."
            )
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while adding user to event: {e}")

    @retry_on_db_error()
    def remove_user_from_event(
        self, db: Session, user_email: String, event_id: int
    ) -> None:
        try:
            user = db.query(User).filter(User.email == user_email).first()
            if not user:
                raise ValueError(f"User with email {user_email} does not exist.")
            user_event = (
                db.query(UserEvent)
                .filter_by(user_id=user.id, event_id=event_id)
                .first()
            )
            if user_event:
                db.delete(user_event)
                db.commit()
            else:
                raise ValueError(
                    f"User with email {user_email} is not registered for event {event_id}."
                )
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while removing user from event: {e}")

    @retry_on_db_error()
    def get_users_for_event(self, db: Session, event_id: int) -> list[User]:
        return (
            db.query(User).join(UserEvent).filter(UserEvent.event_id == event_id).all()
        )

    @retry_on_db_error()
    def get_events_for_user(self, db: Session, user_email: String) -> list[Event]:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise ValueError(f"User with email {user_email} does not exist.")
        return (
            db.query(Event).join(UserEvent).filter(UserEvent.user_id == user.id).all()
        )

    @retry_on_db_error()
    def is_user_registered_for_event(
        self, db: Session, user_email: String, event_id: int
    ) -> bool:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise ValueError(f"User with email {user_email} does not exist.")
        return (
            db.query(UserEvent)
            .filter(UserEvent.user_id == user.id, UserEvent.event_id == event_id)
            .count()
            > 0
        )
