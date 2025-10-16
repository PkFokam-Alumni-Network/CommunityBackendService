from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base

class Upvote(Base):
    __tablename__ = "upvotes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id', ondelete="CASCADE"), nullable=True)
    comment_id = Column(Integer, ForeignKey('comments.id', ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="upvotes")
    post = relationship("Post", back_populates="upvotes")
    comment = relationship("Comment", back_populates="upvotes")

    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_user_post_upvote'),
        UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_upvote'),
    )