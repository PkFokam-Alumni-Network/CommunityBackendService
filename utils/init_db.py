from models.user import User
from models.announcement import Announcement
from database import engine

def create_tables():
    User.metadata.create_all(bind=engine)
    Announcement.metadata.create_all(bind=engine)