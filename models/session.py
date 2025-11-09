from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
from core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone.utc), default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone.utc), default=lambda: datetime.now(timezone.utc) + timedelta(days=7), nullable=False)


    user = relationship("User", back_populates="sessions")
