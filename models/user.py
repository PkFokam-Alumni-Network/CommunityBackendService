from sqlalchemy import Column, String, Integer
from database import Base

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
    image = Column(String)
    linkedin_profile = Column(String)
    bio = Column(String, nullable=True)
