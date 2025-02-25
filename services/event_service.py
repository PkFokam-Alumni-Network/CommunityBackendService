from typing import List
from sqlalchemy.orm import Session
from models.event import Event
from repository.event_repository import EventRepository
from repository.user_event_repository import UserEventRepository
from models.user import User
from schemas.event_schema import EventCreate, EventUpdate
from utils.singleton_meta import SingletonMeta

class EventService(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.event_repository = EventRepository(session=session)
        self.user_event_repository = UserEventRepository(session=session)

    def create_event(self, event_data: EventCreate) -> Event:
        event = Event(
        title=event_data.title,
        start_time=event_data.start_time,
        end_time=event_data.end_time,
        location=event_data.location,
        description=event_data.description,
        categories=event_data.categories
    )
        return self.event_repository.add_event(event)

    def update_event(self, event_id: int, event_data: EventUpdate) -> Event:
        event = self.event_repository.get_event_by_id(event_id)
        if not event:
            raise ValueError("Event not found.")
        for key, value in event_data.model_dump().items():
            setattr(event, key, value)
        return self.event_repository.update_event(event)

    def delete_event(self, event_id: int) -> None:
        self.event_repository.delete_event(event_id)

    def register_user_for_event(self, user_id: int, event_id: int) -> None:
        if self.user_event_repository.is_user_registered_for_event(user_id, event_id):
            raise ValueError("User is already registered for this event.")
        self.user_event_repository.add_user_to_event(user_id, event_id)

    def unregister_user_from_event(self, user_id: int, event_id: int) -> None:
        if not self.user_event_repository.is_user_registered_for_event(user_id, event_id):
            raise ValueError("User is not registered for this event.")
        self.user_event_repository.remove_user_from_event(user_id, event_id)

    def get_event_users(self, event_id: int) -> List[User]:
        return self.user_event_repository.get_users_for_event(event_id)

    def get_user_events(self, user_id: int) -> List[Event]:
        return self.user_event_repository.get_events_for_user(user_id)

    def get_all_events(self) -> List[Event]:
        return self.event_repository.get_events()
    
    def get_event_by_id(self, event_id:int) -> Event:
        return self.event_repository.get_event_by_id(event_id=event_id)