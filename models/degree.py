from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Degree(Base):
    __tablename__ = "degrees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Foreign key to users table
    degree = Column(String, nullable=False)
    major = Column(String, nullable=False)
    graduation_year = Column(Integer, nullable=False)
    location = Column(String, nullable=False)

    # Relationships
    user = relationship("User", back_populates="degrees")