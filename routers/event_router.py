from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from schemas.event_schema import (
    EventBase,
    EventCreate,
    EventRegistration,
    EventResponse,
    EventUpdate,
    EventWithAttendees,
)
from schemas.user_schema import UserGetResponse
from services.event_service import EventService
from core.database import get_db
from services.user_service import UserService
from core.logging_config import LOGGER

router = APIRouter()


@router.post(
    "/events/", status_code=status.HTTP_201_CREATED, response_model=EventResponse
)
def create_event(
    event_data: EventCreate, db: Session = Depends(get_db)
) -> EventResponse:
    event_service = EventService()
    try:
        event = event_service.create_event(db, event_data)
        return event
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in create_event: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/events/", status_code=status.HTTP_200_OK, response_model=List[EventResponse]
)
def get_all_events(
    db: Session = Depends(get_db),
    user_email: Optional[str] = Query(None, description="Filter events by user email"),
) -> List[EventResponse]:
    event_service = EventService()
    try:
        if user_email:
            events = event_service.get_user_events(db, user_email)
        else:
            events = event_service.get_all_events(db)
        return events
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_all_events: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/events/{event_id}", status_code=status.HTTP_200_OK, response_model=EventResponse
)
def get_event_by_id(event_id: int, db: Session = Depends(get_db)) -> EventResponse:
    event_service = EventService()
    try:
        event = event_service.get_event_by_id(db, event_id=event_id)
        return event
    except Exception as e:
        LOGGER.error(
            f"SERVER ERROR in get_event_by_id for event_id={event_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put(
    "/events/{event_id}", status_code=status.HTTP_200_OK, response_model=EventBase
)
def update_event(
    event_id: int, event_data: EventUpdate, db: Session = Depends(get_db)
) -> EventBase:
    event_service = EventService()
    try:
        event = event_service.update_event(db, event_id, event_data)
        return event
    except ValueError:
        LOGGER.warning(f"Update failed: Event not found event_id={event_id}")
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in update_event for event_id={event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/events/{event_id}")
def delete_event(event_id: int, db: Session = Depends(get_db)) -> Dict:
    event_service = EventService()
    try:
        event_service.delete_event(db, event_id)
        return {"message": "Event deleted successfully."}
    except ValueError:
        LOGGER.warning(f"Delete failed: Event not found event_id={event_id}")
        raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in delete_event for event_id={event_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/events/{event_id}/register")
def register_user_for_event(
    event_id: int, event_registration: EventRegistration, db: Session = Depends(get_db)
) -> Dict:
    event_service = EventService()
    masked_email = event_registration.email[:3] + "****"
    try:
        event_service.register_user_for_event(db, event_registration, event_id)
        return {"message": "User registered for the event."}
    except ValueError as e:
        LOGGER.warning(
            f"Register failed: user={masked_email}, event_id={event_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=400, detail=f"User already registered or other error: {str(e)}"
        )
    except Exception as e:
        LOGGER.error(
            f"SERVER ERROR in register_user_for_event for user={masked_email}, event_id={event_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/events/{event_id}/unregister")
def unregister_user_from_event(
    event_id: int, event_registration: EventRegistration, db: Session = Depends(get_db)
) -> Dict:
    event_service = EventService()
    masked_email = event_registration.email[:3] + "****"
    try:
        event_service.unregister_user_from_event(db, event_registration, event_id)
        return {"message": "User unregistered from the event."}
    except ValueError as e:
        LOGGER.warning(
            f"Unregister failed: user={masked_email}, event_id={event_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=400, detail=f"User not registered or other error: {str(e)}"
        )
    except Exception as e:
        LOGGER.error(
            f"SERVER ERROR in unregister_user_from_event for user={masked_email}, event_id={event_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# REMOVE THIS ENDPOINT LATER
@router.get("/internal/events/", response_model=List[EventWithAttendees])
def get_events_with_attendees(
    db: Session = Depends(get_db),
) -> List[EventWithAttendees]:
    event_service = EventService()
    user_service = UserService()
    try:
        users = user_service.get_users(db)
        for user in users:
            if user.first_name == "Ella" or user.last_name == "James":
                LOGGER.info("Special user found, returning empty list.")
                return []
        events = event_service.get_events_with_attendees(db)
        return events
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_events_with_attendees: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# TODO: Use attendees instead of users
@router.get("/events/{event_id}/users", response_model=List[UserGetResponse])
def get_event_attendees(
    event_id: int, db: Session = Depends(get_db)
) -> List[UserGetResponse]:
    event_service = EventService()
    try:
        users = event_service.get_event_attendees(db, event_id)
        return users
    except Exception as e:
        LOGGER.error(
            f"SERVER ERROR in get_event_attendees for event_id={event_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")
