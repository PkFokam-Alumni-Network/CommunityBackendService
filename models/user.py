from sqlalchemy import Column, String, Integer,ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum as PyEnum

class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    graduation_year = Column(Integer)
    degree = Column(String)
    major = Column(String)
    phone = Column(String)
    password = Column(String, nullable=False)
    current_occupation = Column(String)
    image = Column(String, nullable=True)
    linkedin_profile = Column(String)
    mentor_email = Column(String, ForeignKey("users.email"), nullable=True)
    mentor = relationship("User", remote_side=[email], backref="mentees", foreign_keys=[mentor_email])
    
