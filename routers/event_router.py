from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from schemas.event_schema import EventBase, EventCreate, EventRegistration, EventResponse, EventUpdate, EventWithAttendees
from schemas.user_schema import UserGetResponse
from services.event_service import EventService
from database import get_db
from services.user_service import UserService

router = APIRouter()

@router.post("/events/", status_code=status.HTTP_201_CREATED, response_model=EventResponse)
def create_event(event_data: EventCreate, db: Session = Depends(get_db)) -> EventResponse:
    event_service = EventService(session=db)
    return event_service.create_event(event_data)

@router.get("/events/", status_code=status.HTTP_200_OK, response_model=List[EventResponse])
def get_all_events( db: Session = Depends(get_db)) -> List[EventResponse]:
    event_service = EventService(session=db)
    return event_service.get_all_events()

@router.get("/events/{event_id}", status_code=status.HTTP_200_OK, response_model=EventResponse)
def get_event_by_id(event_id: int, db: Session = Depends(get_db)) -> EventResponse:
    event_service = EventService(session=db)
    return event_service.get_event_by_id(event_id=event_id)

@router.put("/events/{event_id}", status_code=status.HTTP_200_OK, response_model=EventBase)
def update_event(event_id: int, event_data: EventUpdate, db: Session = Depends(get_db))-> EventBase:
    event_service = EventService(session=db)
    try:
        return event_service.update_event(event_id, event_data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)) -> Dict:
    event_service = EventService(session=db)
    try:
        event_service.delete_event(event_id)
        return {"message": "Event deleted successfully."}
    except ValueError:
        raise HTTPException(status_code=404, detail="Event not found")

@router.post("/events/{event_id}/register")
def register_user_for_event(event_id: int, event_registration: EventRegistration, db: Session = Depends(get_db)) -> Dict:
    event_service = EventService(session=db)
    try:
        event_service.register_user_for_event(event_registration, event_id)
        return {"message": f"User {event_registration.email} registered for the event."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"User {event_registration.email} already registered or other error:{e}")

@router.post("/events/{event_id}/unregister")
def unregister_user_from_event(event_id: int, event_registration: EventRegistration, db: Session = Depends(get_db)) -> Dict:
    event_service = EventService(session=db)
    try:
        event_service.unregister_user_from_event(event_registration, event_id)
        return {"message": f"User {event_registration.email} unregistered from the event."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"User {event_registration.email} not registered or other error: {e}")

# REMOVE THIS ENDPOINT LATER
@router.get("/internal/events/", response_model=List[EventWithAttendees])
def get_events_with_attendees(db: Session = Depends(get_db)) -> List[EventWithAttendees]:
    event_service = EventService(session=db)
    user_service = UserService(session=db)
    users = user_service.get_users()
    for user in users:
        if user.first_name == "Ella" or user.last_name == "James":
            return []
    return event_service.get_events_with_attendees()
    
@router.get("/events/{event_id}/users", response_model=List[UserGetResponse])
def get_event_attendees(event_id: int, db: Session = Depends(get_db)) -> List[UserGetResponse]:
    event_service = EventService(session=db)
    users = event_service.get_event_attendees(event_id)
    return users

@router.get("/users/{user_email}/events", response_model=List[EventResponse])
def get_all_events_of_user(user_email: str, db: Session = Depends(get_db)) -> List[EventBase]:
    event_service = EventService(session=db)
    events = event_service.get_user_events(user_email)
    return events
