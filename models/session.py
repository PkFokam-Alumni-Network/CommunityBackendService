from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
try:
    from database import Base
except ImportError:
    from ..database import Base
from datetime import datetime, timezone

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_type = Column(String, nullable=True, default="unknown")
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False) 
    is_active = Column(Boolean, default=True, nullable=False)
    
    user = relationship("User", back_populates="sessions")