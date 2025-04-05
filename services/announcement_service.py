from typing import Optional
from sqlalchemy.orm import Session
from repository.announcement_repository import AnnouncementRepository
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from services.user_service import UserService
from utils.func_utils import send_bulk_emails

class AnnouncementService:

    def __init__(self, session: Session):
        self.repository = AnnouncementRepository(session)

    def create_announcement(self, announcement: AnnouncementCreate) -> AnnouncementResponse:
        if self.repository.get_announcement_by_title(announcement.title):
            raise ValueError("Announcement with this title already exists.")

        if announcement.announcement_deadline and announcement.announcement_date > announcement.announcement_deadline:
            raise ValueError("Announcement date must be before announcement deadline.")

        db_announcement = self.repository.add_announcement(announcement)
        return AnnouncementResponse.model_validate(db_announcement)

    def get_all_announcements(self) -> list[AnnouncementCreate]:
        announcements = self.repository.get_announcements()
        return [AnnouncementCreate.model_validate(announcement) for announcement in announcements]

    def get_announcement_by_id(self, announcement_id: int) -> Optional[AnnouncementCreate]:
        db_announcement = self.repository.get_announcement_by_id(announcement_id)
        return AnnouncementCreate.model_validate(db_announcement)

    def update_announcement(self, announcement_id: int, announcement: AnnouncementUpdate) -> Optional[
        AnnouncementCreate]:
        updated_announcement = self.repository.update_announcement(announcement_id, announcement)
        return AnnouncementCreate.model_validate(updated_announcement)

    def delete_announcement(self, announcement_id: int) -> None:
        announcement = self.repository.delete_announcement(announcement_id)
        if not announcement:
            raise ValueError("Announcement not found")
    
            
        
        

