from sqlalchemy import Integer, Column, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base
import enum

class ResumeStatus(enum.Enum):
    pending = "PENDING"
    in_review = "IN-REVIEW"
    reviewed = "REVIEWED"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key= True )
    user_id = Column(Integer, ForeignKey('users.id', ondelete= "CASCADE"), nullable= False)
    file_name = Column(Text, nullable = False)
    file_path = Column(Text, nullable = False)
    status = Column(Enum(ResumeStatus), default = ResumeStatus.pending, nullable= False)
    uploaded_at = Column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc), nullable = False)
    updated_at = Column(DateTime(timezone = True), default = lambda: datetime.now(timezone.utc), onupdate = lambda: datetime.now(timezone.utc), nullable = False)

    user = relationship("User", back_populates="resumes")
    reviews = relationship("ResumeReview", back_populates="resume", cascade="all, delete-orphan")