from sqlalchemy import Integer, ForeignKey, Column
from sqlalchemy.orm import relationship
from core.database import Base


class UserEvent(Base):
    __tablename__ = "user_events"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )

    user = relationship("User", back_populates="user_events")
    event = relationship("Event", back_populates="user_events")
