from pydantic import BaseModel, ConfigDict
from datetime import datetime

class PostCreate(BaseModel):
    author_id: int
    title: str
    content: str
    category: str

class PostResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
