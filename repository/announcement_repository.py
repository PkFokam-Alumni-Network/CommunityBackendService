from typing import Optional, Type
from sqlalchemy.orm import Session
from models.announcement import Announcement
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate
from utils.retry import retry_on_db_error


class AnnouncementRepository():
    @retry_on_db_error()
    def add_announcement(
        self, db: Session, announcement: AnnouncementCreate
    ) -> Announcement:
        db_announcement = Announcement(**announcement.model_dump())
        db.add(db_announcement)
        db.commit()
        db.refresh(db_announcement)
        return db_announcement

    @retry_on_db_error()
    def get_announcements(self, db: Session) -> list[Type[Announcement]]:
        return db.query(Announcement).order_by(Announcement.announcement_date.desc()).all()

    @retry_on_db_error()
    def get_announcement_by_id(
        self, db: Session, announcement_id: int
    ) -> Optional[Announcement]:
        return db.query(Announcement).filter(Announcement.id == announcement_id).first()

    @retry_on_db_error()
    def update_announcement(
        self, db: Session, announcement_id: int, announcement: AnnouncementUpdate
    ) -> Optional[Announcement]:
        db_announcement = self.get_announcement_by_id(db, announcement_id)
        if db_announcement:
            for key, value in announcement.model_dump().items():
                setattr(db_announcement, key, value)
            db.commit()
            db.refresh(db_announcement)
        return db_announcement

    @retry_on_db_error()
    def delete_announcement(
        self, db: Session, announcement_id: int
    ) -> Optional[Announcement]:
        db_announcement = self.get_announcement_by_id(db, announcement_id)
        if db_announcement:
            db.delete(db_announcement)
            db.commit()
        return db_announcement

    @retry_on_db_error()
    def get_announcement_by_title(
        self, db: Session, title: str
    ) -> Optional[Announcement]:
        return db.query(Announcement).filter(Announcement.title == title).first()
