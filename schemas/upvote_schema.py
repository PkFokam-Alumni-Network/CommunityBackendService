from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UpvoteResponse(BaseModel):
    id: int
    user_id: int
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UpvoteCreatedResponse(BaseModel):
    message: str
    upvote: UpvoteResponse

class UpvoteDeletedResponse(BaseModel):
    message: str