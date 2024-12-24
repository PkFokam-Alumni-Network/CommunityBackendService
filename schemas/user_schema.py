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
    mentor_email: Optional[EmailStr] = None
    
class UserCreatedResponse(BaseModel):
    email: str
    first_name: str
    last_name: str
    mentor_email: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserDeletedResponse(BaseModel):
    message: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    graduation_year: Optional[int] = None
    degree: Optional[str] = None
    major: Optional[str] = None
    phone: Optional[str] = None
    current_occupation: Optional[str] = None
    image: Optional[str] = None
    linkedin_profile: Optional[str] = None
    mentor_email: Optional[EmailStr] = None

class UserEmailUpdate(BaseModel):
    email: EmailStr

