from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base
from models.enums import AttachmentType

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    attachment_url = Column(String(500), nullable=True)
    attachment_type = Column(Enum(AttachmentType), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    upvotes = relationship("Upvote", back_populates="comment", cascade="all, delete-orphan")