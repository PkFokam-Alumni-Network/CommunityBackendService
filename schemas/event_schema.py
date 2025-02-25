from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

class EventBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    description: Optional[str] = None
    categories: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

class EventWithAttendees(EventResponse):
    attendees: Optional[List[int]]
