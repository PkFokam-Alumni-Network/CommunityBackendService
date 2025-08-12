from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from core.database import Base
from datetime import datetime, timezone

class ResumeReview(Base):
    __tablename__ = "resume_reviews"

    id = Column(Integer, primary_key= True, autoincrement= True)
    resume_id = Column(Integer, ForeignKey('resumes.id', ondelete = 'CASCADE'), nullable= False)
    reviewer_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'), nullable = False)
    comments = Column(Text, nullable = False)
    reviewed_at = Column(DateTime(timezone=True), default = lambda: datetime.now(timezone.utc), nullable = False)

    resume = relationship("Resume", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")
    