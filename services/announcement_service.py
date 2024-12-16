from typing import Optional, List, Type
from sqlalchemy.orm import Session
from models.announcement import Announcement
from repository.announcement_repository import AnnouncementRepository
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse


class AnnouncementService:

    def __init__(self, session: Session):
        self.repository = AnnouncementRepository(session)

    def create_announcement(self, announcement: AnnouncementCreate) -> AnnouncementResponse:
        # check if announcement already exists
        if self.repository.get_announcement_by_title(announcement.title):
            raise ValueError("Announcement with this title already exists.")

        # Check if announcement date is before announcement deadline
        if announcement.announcement_date >= announcement.announcement_deadline:
            raise ValueError("Announcement date must be before announcement deadline.")

        return AnnouncementResponse.from_orm(self.repository.add_announcement(announcement))

    def get_all_announcements(self) -> list[AnnouncementCreate]:
        announcements = self.repository.get_announcements()
        return [AnnouncementCreate.from_orm(announcement) for announcement in announcements]

    def get_announcement_by_id(self, announcement_id: int) -> Optional[AnnouncementCreate]:
        return AnnouncementCreate.from_orm(self.repository.get_announcement_by_id(announcement_id))

    def update_announcement(self, announcement_id: int, announcement: AnnouncementUpdate) -> Optional[
        AnnouncementUpdate]:
        return AnnouncementUpdate.from_orm(self.repository.update_announcement(announcement_id, announcement))

    def delete_announcement(self, announcement_id: int) -> None:
        announcement = self.repository.delete_announcement(announcement_id)
        if not announcement:
            raise ValueError("Announcement not found")
