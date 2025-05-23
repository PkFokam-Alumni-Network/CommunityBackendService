from sqlalchemy import Integer, ForeignKey, Column, Text
from sqlalchemy.orm import relationship
from database import Base

class UserEvent(Base):
    __tablename__ = 'user_events'

    user_email= Column(Text, ForeignKey('users.email', ondelete="CASCADE"), primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id',  ondelete="CASCADE"), primary_key=True)
    
    user = relationship("User", back_populates="user_events")
    event = relationship("Event", back_populates="user_events")