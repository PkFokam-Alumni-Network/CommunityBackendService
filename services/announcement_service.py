from typing import Optional
from sqlalchemy.orm import Session
from repository.announcement_repository import AnnouncementRepository
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse


class AnnouncementService:

    def __init__(self, session: Session):
        self.repository = AnnouncementRepository(session)

    def create_announcement(self, announcement: AnnouncementCreate) -> AnnouncementResponse:
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
        AnnouncementCreate]:
        updated_announcement = self.repository.update_announcement(announcement_id, announcement)
        return AnnouncementCreate.model_validate(updated_announcement)

    def delete_announcement(self, announcement_id: int) -> None:
        announcement = self.repository.delete_announcement(announcement_id)
        if not announcement:
            raise ValueError("Announcement not found")
