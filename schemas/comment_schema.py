from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from models.enums import AttachmentType

class CommentCreate(BaseModel):
    content: str
    attachment: Optional[str] = None # can be base64 image or a giphy link
    attachment_type: Optional[AttachmentType] = None

    @model_validator(mode='after')
    def validate_attachments(self):
        if self.attachment_type and not self.attachment:
            raise ValueError("attachment is required when attachment_type is provided")
        return self

class CommentUpdate(BaseModel):
    content: str
    attachment: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None

class CommentResponse(BaseModel):
    id: int
    post_id: int
    author_id: int
    content: str
    attachment_url: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None
    created_at: datetime
    updated_at: datetime
    upvote_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class CommentDeletedResponse(BaseModel):
    message: str