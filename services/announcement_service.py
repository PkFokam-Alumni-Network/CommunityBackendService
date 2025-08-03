from typing import Optional
from sqlalchemy.orm import Session
from repository.announcement_repository import AnnouncementRepository
from schemas.announcement_schema import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
)


class AnnouncementService:
    def create_announcement(
        self, db: Session, announcement: AnnouncementCreate
    ) -> AnnouncementResponse:
        repository = AnnouncementRepository()
        if repository.get_announcement_by_title(db, announcement.title):
            raise ValueError("Announcement with this title already exists.")

        if (
            announcement.announcement_deadline
            and announcement.announcement_date > announcement.announcement_deadline
        ):
            raise ValueError("Announcement date must be before announcement deadline.")

        db_announcement = repository.add_announcement(db, announcement)
        return AnnouncementResponse.model_validate(db_announcement)

    def get_all_announcements(self, db: Session) -> list[AnnouncementCreate]:
        repository = AnnouncementRepository()
        announcements = repository.get_announcements(db)
        return [
            AnnouncementCreate.model_validate(announcement)
            for announcement in announcements
        ]

    def get_announcement_by_id(
        self, db: Session, announcement_id: int
    ) -> Optional[AnnouncementCreate]:
        repository = AnnouncementRepository()
        db_announcement = repository.get_announcement_by_id(db, announcement_id)
        return AnnouncementCreate.model_validate(db_announcement)

    def update_announcement(
        self, db: Session, announcement_id: int, announcement: AnnouncementUpdate
    ) -> Optional[AnnouncementCreate]:
        repository = AnnouncementRepository()
        updated_announcement = repository.update_announcement(
            db, announcement_id, announcement
        )
        return AnnouncementCreate.model_validate(updated_announcement)

    def delete_announcement(self, db: Session, announcement_id: int) -> None:
        repository = AnnouncementRepository()
        announcement = repository.delete_announcement(db, announcement_id)
        if not announcement:
            raise ValueError("Announcement not found")
