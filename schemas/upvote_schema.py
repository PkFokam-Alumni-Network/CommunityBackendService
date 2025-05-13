from pydantic import BaseModel
from datetime import datetime

class UpvoteCreate(BaseModel):
    user_id: int
    post_id: int

class UpvoteResponse(UpvoteCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
