import enum
from sqlalchemy import Boolean, Column, Enum, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    image = Column(String, nullable=True)
    bio = Column(String)
    graduation_year = Column(Integer)
    degree = Column(String)
    major = Column(String)
    current_occupation = Column(String)
    mentor_email = Column(String, ForeignKey("users.email"), nullable=True)
    mentor = relationship("User", remote_side=[email], backref="mentees", foreign_keys=[mentor_email])
    is_active = Column(Boolean, default=True)
    linkedin_profile = Column(String)
    instagram_profile = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)

    user_events = relationship("UserEvent", back_populates="user")
    posts = relationship("Post", back_populates="author")
    
