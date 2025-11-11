from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base

class UserJourney(Base):
    __tablename__ = "user_journeys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String, index=True)
    action = Column(String, nullable=False, index=True)  # e.g., "login", "view_post", "create_comment"
    endpoint = Column(String)
    method = Column(String) 
    extra_metadata = Column(JSON)  # Additional context (e.g., post_id, comment_id)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", backref="journey_logs")

    def __repr__(self):
        return f"<UserJourney(user_id={self.user_id}, action={self.action}, timestamp={self.timestamp})>"