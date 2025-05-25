from typing import Type, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from services.announcement_service import AnnouncementService
from models.announcement import Announcement
from logging_config import LOGGER

router = APIRouter()

@router.post("/announcements/", status_code=status.HTTP_201_CREATED, response_model=AnnouncementResponse)
def create_announcement(announcement: AnnouncementCreate, session: Session = Depends(get_db)) -> AnnouncementResponse:
    service = AnnouncementService()
    try:
        ann = service.create_announcement(session, announcement)
        return ann
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in create_announcement: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/announcements/", status_code=status.HTTP_200_OK, response_model=list[AnnouncementCreate])
def get_all_announcements(session: Session = Depends(get_db)) -> list[AnnouncementCreate]:
    service = AnnouncementService()
    try:
        anns = service.get_all_announcements(session)
        return anns
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_all_announcements: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/announcements/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementCreate)
def get_announcement_by_id(announcement_id: int, session: Session = Depends(get_db)) -> Announcement:
    service = AnnouncementService()
    try:
        ann = service.get_announcement_by_id(session, announcement_id)
        return ann
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_announcement_by_id for id={announcement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/announcements/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementCreate)
def update_announcement(announcement_id: int, announcement: AnnouncementUpdate,
    session: Session = Depends(get_db)) -> AnnouncementUpdate:
    service = AnnouncementService()
    try:
        ann = service.update_announcement(session, announcement_id, announcement)
        return ann
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in update_announcement for id={announcement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_200_OK, response_model=AnnouncementResponse)
def delete_announcement(announcement_id: int, session: Session = Depends(get_db)) -> AnnouncementResponse:
    service = AnnouncementService()
    try:
        service.delete_announcement(session, announcement_id)
        LOGGER.info(f"Announcement deleted: id={announcement_id}")
        return AnnouncementResponse(id=announcement_id, message="Announcement deleted successfully.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in delete_announcement for id={announcement_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")