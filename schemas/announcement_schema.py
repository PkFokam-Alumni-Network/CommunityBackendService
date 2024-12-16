# schemas/announcement_schema.py
from pydantic import BaseModel, root_validator, model_validator, ConfigDict
from typing import Optional
from datetime import datetime


class AnnouncementCreate(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    announcement_date: datetime
    announcement_deadline: Optional[datetime] = None
    image: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


class AnnouncementUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    announcement_date: Optional[datetime] = None
    announcement_deadline: Optional[datetime] = None
    image: Optional[str] = None

    #model_config = ConfigDict(from_attributes=True)

    class Config:
        orm_mode = True
        from_attributes = True


class AnnouncementResponse(BaseModel):
    id: Optional[int] = None
    message: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

    #model_config = ConfigDict(from_attributes=True)
