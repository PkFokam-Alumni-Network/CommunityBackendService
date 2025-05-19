from models.user import User
from models.announcement import Announcement
from models.user_event import UserEvent
from models.event import Event
from models.degree import Degree
from database import engine

def create_tables():
    User.metadata.create_all(bind=engine)
    Announcement.metadata.create_all(bind=engine)
    Event.metadata.create_all(bind=engine)
    UserEvent.metadata.create_all(bind=engine)
    Degree.metadata.create_all(bind=engine)