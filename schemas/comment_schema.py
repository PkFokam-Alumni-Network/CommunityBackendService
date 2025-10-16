from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    content: str

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    upvote_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class CommentDeletedResponse(BaseModel):
    message: str