from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from models.enums import AttachmentType

class Author(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None

class PostCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = None
    attachment: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None

    @model_validator(mode='after')
    def validate_attachments(self):
        if self.attachment_type and not self.attachment:
            raise ValueError("attachment is required when attachment_type is provided")
        return self

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    attachment: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str] = None
    attachment_url: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None
    author: Author
    created_at: datetime
    updated_at: datetime
    upvote_count: int
    comment_count: int
    liked_by_user: bool = False # default if unauthenticated

    model_config = ConfigDict(from_attributes=True)

class PostDeletedResponse(BaseModel):
    message: str
