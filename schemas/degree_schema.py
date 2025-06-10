from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class DegreeCreate(BaseModel):
    degree: str
    major: str
    graduation_year: int
    location: str
    
class DegreeResponse(BaseModel):
    id: int
    degree: str
    major: str
    graduation_year: int
    location: str
    
    model_config = ConfigDict(from_attributes=True)