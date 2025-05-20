from pydantic import BaseModel, Literal
from datetime import datetime

class UpvoteCreate(BaseModel):
    user_id: int
    post_id: int

class UpvoteToggleResponse(BaseModel):
    user_id: int
    post_id: int
    action: Literal["added", "removed"]

    model_config = ConfigDict(from_attributes=True)

class UpvoteCountResponse(BaseModel):
    post_id: int
    upvotes: int