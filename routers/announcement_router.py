from typing import Type, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from services.announcement_service import AnnouncementService
from models.announcement import Announcement

router = APIRouter()


@router.post("/announcements/", status_code=status.HTTP_201_CREATED, response_model=AnnouncementResponse)
def create_announcement(announcement: AnnouncementCreate, session: Session = Depends(get_db)) -> AnnouncementResponse:
    service = AnnouncementService(session=session)
    try:
        return service.create_announcement(announcement)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/announcements/", status_code=status.HTTP_200_OK, response_model=list[AnnouncementCreate])
def get_all_announcements(session: Session = Depends(get_db)) -> list[AnnouncementCreate]:
    service = AnnouncementService(session=session)
    return service.get_all_announcements()


@router.get("/announcements/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementCreate)
def get_announcement_by_id(announcement_id: int, session: Session = Depends(get_db)) -> Announcement:
    service = AnnouncementService(session=session)
    try:
        return service.get_announcement_by_id(announcement_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/announcements/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementCreate)
def update_announcement(announcement_id: int, announcement: AnnouncementUpdate,
                        session: Session = Depends(get_db)) -> AnnouncementUpdate:
    service = AnnouncementService(session=session)
    try:
        return service.update_announcement(announcement_id, announcement)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementResponse)
def delete_announcement(announcement_id: int, session: Session = Depends(get_db)) -> AnnouncementResponse:
    service = AnnouncementService(session=session)
    try:
        service.delete_announcement(announcement_id)
        return AnnouncementResponse(id=announcement_id, message="Announcement deleted successfully.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))