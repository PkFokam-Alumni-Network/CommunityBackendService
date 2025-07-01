from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PostCreate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class PostUpdate(BaseModel):
    title: str
    content: str
    category: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PostDeletedResponse(BaseModel):
    message: str
