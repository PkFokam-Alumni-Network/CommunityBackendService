from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional

from schemas.user_schema import Attendee, UserGetResponse

class EventBase(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    description: Optional[str] = None
    categories: Optional[str] = None
    image: Optional[str] = "https://cdn-cjhkj.nitrocdn.com/krXSsXVqwzhduXLVuGLToUwHLNnSxUxO/assets/images/optimized/rev-b135bb1/spotme.com/wp-content/uploads/2020/07/Hero-1.jpg"

    model_config = ConfigDict(from_attributes=True)

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class EventResponse(EventBase):
    id: int

class EventWithAttendees(EventResponse):
    attendees: Optional[List[Attendee]]

class EventRegistration(BaseModel):
    email: EmailStr
