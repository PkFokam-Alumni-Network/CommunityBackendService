from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class DegreeResponse(BaseModel):
    id: int
    degree: str
    major: str
    graduation_year: int
    location: str
    
    model_config = ConfigDict(from_attributes=True)