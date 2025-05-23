from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Session
from models.event import Event
from repository.event_repository import EventRepository
from repository.user_event_repository import UserEventRepository
from models.user import User
from schemas.event_schema import EventCreate, EventRegistration, EventUpdate, EventWithAttendees
from utils.singleton_meta import SingletonMeta

class EventService(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.event_repository = EventRepository(session=session)
        self.user_event_repository = UserEventRepository(session=session)

    def create_event(self, event_data: EventCreate) -> Event:
        event_data_dict = event_data.model_dump()
        event = Event(**event_data_dict)
        return self.event_repository.add_event(event)
    def update_event(self, event_id: int, event_data: EventUpdate) -> Event:
        event = self.event_repository.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        for key, value in event_data.model_dump().items():
            setattr(event, key, value)
        return self.event_repository.update_event(event)

    def delete_event(self, event_id: int) -> None:
        event = self.event_repository.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        self.event_repository.delete_event(event_id)

    # TODO: Add validation for event existence
    def register_user_for_event(self, event_registration: EventRegistration, event_id: int) -> None:
        user_email = event_registration.email
        if self.user_event_repository.is_user_registered_for_event(user_email, event_id):
            raise ValueError("User is already registered for this event.")
        self.user_event_repository.add_user_to_event(user_email, event_id)

    def unregister_user_from_event(self, event_registration: EventRegistration, event_id: int) -> None:
        user_email = event_registration.email
        if not self.user_event_repository.is_user_registered_for_event(user_email, event_id):
            raise ValueError("User is not registered for this event.")
        self.user_event_repository.remove_user_from_event(user_email, event_id)

    def get_event_attendees(self, event_id: int) -> List[User]:
        return self.user_event_repository.get_users_for_event(event_id)

    def get_user_events(self, user_email: String) -> List[Event]:
        return self.user_event_repository.get_events_for_user(user_email)

    def get_all_events(self) -> List[Event]:
        return self.event_repository.get_events()
    
    def get_event_by_id(self, event_id:int) -> Event:
        return self.event_repository.get_event_by_id(event_id=event_id)
    
    def get_events_with_attendees(self) -> List[EventWithAttendees]:
        events = self.event_repository.get_events()
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
                attendees=self.get_event_attendees(event.id)
            )
            for event in events
        ]
