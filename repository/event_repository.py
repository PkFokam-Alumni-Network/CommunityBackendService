from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models.event import Event
from utils.retry import retry_on_db_error


class EventRepository():
    @retry_on_db_error()
    def add_event(self, db: Session, event: Event) -> Event:
        try:
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        except IntegrityError:
            db.rollback()
            raise ValueError("Event with the same details already exists.")
        except OperationalError as e:
            db.rollback()
            raise ConnectionError("Database connection error: " + str(e))
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def get_event_by_id(self, db: Session, event_id: int) -> Event:
        return db.query(Event).filter(Event.id == event_id).first()

    @retry_on_db_error()
    def get_events(self, db: Session) -> list[Event]:
        return db.query(Event).all()

    @retry_on_db_error()
    def update_event(self, db: Session, event: Event) -> Event:
        try:
            db.merge(event)
            db.commit()
            db.refresh(event)
            return event
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def delete_event(self, db: Session, event_id: int) -> None:
        event = self.get_event_by_id(db, event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found.")
        try:
            db.delete(event)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(
                f"Unable to delete event with id {event_id} due to integrity constraints."
            )
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while deleting the event: {e}")
