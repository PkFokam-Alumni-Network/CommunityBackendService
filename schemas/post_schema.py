from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional
from models.enums import AttachmentType


class Author(BaseModel):
    id: int
    first_name: str
    last_name: str
    image: Optional[str] = None
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
    category: str
    attachment_url: Optional[str] = None
    attachment_type: Optional[AttachmentType] = None
    author_id: int
    created_at: datetime
    updated_at: datetime
    upvote_count: Optional[int] = 0
    author: Author
    model_config = ConfigDict(from_attributes=True)

class PostDeletedResponse(BaseModel):
    message: str
