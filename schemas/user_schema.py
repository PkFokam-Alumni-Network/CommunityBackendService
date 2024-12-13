from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    graduation_year: Optional[int] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    phone: Optional[str] = None
    current_occupation: Optional[str] = None
    image: Optional[str] = None
    linkedin_profile: Optional[str] = None
    mentor_email: Optional[str] = None

class UserCreatedResponse(BaseModel):
    email: str
    first_name: str
    last_name: str
    
    model_config = ConfigDict(from_attributes=True)

class UserDeletedResponse(BaseModel):
    message: str
