from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    author_id: int
    title: str
    content: str
    category: str

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostDeletedResponse(BaseModel):
    message: str
