from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Session
from models.event import Event
from repository.event_repository import EventRepository
from repository.user_event_repository import UserEventRepository
from models.user import User
from schemas.event_schema import EventCreate, EventRegistration, EventUpdate, EventWithAttendees
from utils.singleton_meta import SingletonMeta
from datetime import datetime

class EventService(metaclass=SingletonMeta):
    def create_event(self, db: Session, event_data: EventCreate) -> Event:
        event_repository = EventRepository()
        event_data_dict = event_data.model_dump()
        event = Event(**event_data_dict)
        return event_repository.add_event(db, event)

    def update_event(self, db: Session, event_id: int, event_data: EventUpdate) -> Event:
        event_repository = EventRepository()
        event = event_repository.get_event_by_id(db, event_id)
        if not event:
            raise ValueError("Event not found.")
        for key, value in event_data.model_dump().items():
            setattr(event, key, value)
        return event_repository.update_event(db, event)

    def delete_event(self, db: Session, event_id: int) -> None:
        event_repository = EventRepository()
        event = event_repository.get_event_by_id(db, event_id)
        
        if not event:
            raise ValueError("Event not found.")
        event_repository.delete_event(db, event_id)

    def register_user_for_event(self, db: Session, event_registration: EventRegistration, event_id: int) -> None:
        user_event_repository = UserEventRepository()
        user_email = event_registration.email
        event_repository = EventRepository()
        event = event_repository.get_event_by_id(db, event_id)
        if not event:
            raise ValueError("Event not found.")

        current_time = datetime.utcnow()
        if event.end_time < current_time:
            raise ValueError("Cannot register for past events.")
        
        if user_event_repository.is_user_registered_for_event(db, user_email, event_id):
            raise ValueError("User is already registered for this event.")
        user_event_repository.add_user_to_event(db, user_email, event_id)

    def unregister_user_from_event(self, db: Session, event_registration: EventRegistration, event_id: int) -> None:
        user_event_repository = UserEventRepository()
        user_email = event_registration.email
        if not user_event_repository.is_user_registered_for_event(db, user_email, event_id):
            raise ValueError("User is not registered for this event.")
        user_event_repository.remove_user_from_event(db, user_email, event_id)

    def get_event_attendees(self, db: Session, event_id: int) -> List[User]:
        user_event_repository = UserEventRepository()
        return user_event_repository.get_users_for_event(db, event_id)

    def get_user_events(self, db: Session, user_email: String) -> List[Event]:
        user_event_repository = UserEventRepository()
        return user_event_repository.get_events_for_user(db, user_email)

    def get_all_events(self, db: Session) -> List[Event]:
        event_repository = EventRepository()
        return event_repository.get_events(db)
    
    def get_event_by_id(self, db: Session, event_id:int) -> Event:
        event_repository = EventRepository()
        return event_repository.get_event_by_id(db, event_id=event_id)
    
    def get_events_with_attendees(self, db: Session) -> List[EventWithAttendees]:
        event_repository = EventRepository()
        user_event_repository = UserEventRepository()
        events = event_repository.get_events(db)
        return [
            EventWithAttendees(
                id=event.id,
                title=event.title,
                start_time=event.start_time,
                end_time=event.end_time,
                location=event.location,
                description=event.description,
                categories=event.categories,
                image=event.image,
                attendees=user_event_repository.get_users_for_event(db, event.id)
            )
            for event in events
        ]
