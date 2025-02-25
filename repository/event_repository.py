from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models.event import Event
from utils.singleton_meta import SingletonMeta

class EventRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def add_event(self, event: Event) -> Event:
        try:
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Event with the same details already exists.")
        except OperationalError as e:
            self.db.rollback()
            raise ConnectionError("Database connection error: " + str(e))
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    def get_event_by_id(self, event_id: int) -> Event:
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_events(self) -> list[Event]:
        return self.db.query(Event).all()

    def update_event(self, event: Event) -> Event:
        try:
            self.db.merge(event)
            self.db.commit()
            self.db.refresh(event)
            return event
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    def delete_event(self, event_id: int) -> None:
        event = self.get_event_by_id(event_id)
        if not event:
            raise ValueError(f"Event with id {event_id} not found.")
        
        try:
            self.db.delete(event)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Unable to delete event with id {event_id} due to integrity constraints.")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred while deleting the event: {e}")
