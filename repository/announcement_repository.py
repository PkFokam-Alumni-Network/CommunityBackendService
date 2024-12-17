from typing import Optional, Type
from sqlalchemy.orm import Session
from models.announcement import Announcement
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate
from utils.singleton_meta import SingletonMeta


class AnnouncementRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.session = session

    def add_announcement(self, announcement: AnnouncementCreate) -> Announcement:
        db_announcement = Announcement(**announcement.model_dump())
        self.session.add(db_announcement)
        self.session.commit()
        self.session.refresh(db_announcement)
        return db_announcement

    def get_announcements(self) -> list[Type[Announcement]]:
        return self.session.query(Announcement).all()

    def get_announcement_by_id(self, announcement_id: int) -> Optional[Announcement]:
        return self.session.query(Announcement).filter(Announcement.id == announcement_id).first()

    def update_announcement(self, announcement_id: int, announcement: AnnouncementUpdate) -> Optional[Announcement]:
        db_announcement = self.get_announcement_by_id(announcement_id)
        if db_announcement:
            for key, value in announcement.model_dump().items():
                setattr(db_announcement, key, value)
            self.session.commit()
            self.session.refresh(db_announcement)
        return db_announcement

    def delete_announcement(self, announcement_id: int) -> Optional[Announcement]:
        db_announcement = self.get_announcement_by_id(announcement_id)
        if db_announcement:
            self.session.delete(db_announcement)
            self.session.commit()
        return db_announcement

    def get_announcement_by_title(self, title: str) -> Optional[Announcement]:
        return self.session.query(Announcement).filter(Announcement.title == title).first()