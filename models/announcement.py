from sqlalchemy import Column, Integer, Text, DateTime
from core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, unique=True)
    description = Column(Text)
    announcement_date = Column(DateTime)
    announcement_deadline = Column(DateTime, nullable=True)
    image = Column(Text, nullable=True)
