from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, CommentDeletedResponse
from services.comment_service import CommentService
from core.database import get_db
from core.logging_config import LOGGER
from core.auth import get_current_user
from models import User

router = APIRouter( tags=["Comments"])
comment_service = CommentService()

@router.post("/comments/", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    comment = comment_service.add_comment(db = session, post_id = post_id, comment_data = comment_data, user_id = current_user.id)
    response = CommentResponse.model_validate(comment)
    LOGGER.info(f"Comment created: {comment}")
    return response

@router.get("/post/{post_id}/comments", status_code=status.HTTP_200_OK, response_model=List[CommentResponse])
def get_comments_by_post(
    post_id: int,
    session: Session = Depends(get_db)
) -> List[CommentResponse]:
    return comment_service.get_comments_by_post_id(db = session, post_id = post_id)

@router.get("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
def get_comment(
    comment_id: int,
    session: Session = Depends(get_db)
) -> CommentResponse:
    comment = comment_service.get_comment_by_id(db = session, comment_id = comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    response = CommentResponse.model_validate(comment)
    LOGGER.info(f"Comment retrieved: {comment}")
    return response

@router.put("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    try:
        comment = comment_service.update_comment(db = session, comment_id = comment_id, user_id = current_user.id, updated_data=comment_data)
        response = CommentResponse.model_validate(comment)
        LOGGER.info(f"Comment updated: {comment}")
        return response
    except ValueError as e:
        LOGGER.error(f"Comment not found: {comment_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        LOGGER.error(f"Not authorized to update comment: {comment_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentDeletedResponse)
def delete_comment(
    comment_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentDeletedResponse:
    try:
        comment_service.delete_comment(db = session, comment_id = comment_id, user_id = current_user.id)
        LOGGER.info(f"Comment deleted: {comment_id}")
        return CommentDeletedResponse(message=f"Comment with ID {comment_id} was successfully deleted")
    except ValueError as e:
        LOGGER.error(f"Comment not found: {comment_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        LOGGER.error(f"Not authorized to delete comment: {comment_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))