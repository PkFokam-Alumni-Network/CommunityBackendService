import enum
from sqlalchemy import Boolean, Column, Enum, Text, Integer,ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, nullable=False, unique=True, index=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    address = Column(Text)
    phone = Column(Text)
    image = Column(Text, nullable=True)
    bio = Column(Text)
    graduation_year = Column(Integer)
    degree = Column(Text)
    major = Column(Text)
    current_occupation = Column(Text)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    linkedin_profile = Column(Text)
    instagram_profile = Column(Text, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)

    posts = relationship("Post", back_populates="author")
    # comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    mentor = relationship("User", remote_side=[id], backref="mentees", foreign_keys=[mentor_id])
    user_events = relationship("UserEvent", back_populates="user", cascade="all, delete-orphan")
