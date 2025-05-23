from sqlalchemy import Column, Integer, Text, Text, DateTime
from sqlalchemy.orm import relationship
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(Text, nullable=True)
    categories = Column(Text)  # Stored as comma separated values
    
    user_events = relationship("UserEvent", back_populates="event")

