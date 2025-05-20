from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    post_id: int
    author_id: int
    content: str

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(CommentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CommentDeletedResponse(BaseModel):
    message: str