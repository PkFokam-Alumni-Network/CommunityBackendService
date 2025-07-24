# Import all models here to ensure they're loaded and available for SQLAlchemy otherwise the relationship might map in disorder
from .user import User
from .event import Event
from .user_event import UserEvent
from .announcement import Announcement
from core.database import Base

__all__ = [
    "Base",
    "User",
    "Event",
    "UserEvent",
    "Announcement",
]