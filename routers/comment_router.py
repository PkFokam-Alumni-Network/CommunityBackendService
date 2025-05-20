from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, CommentDeletedResponse
from services.comment_service import CommentService
from database import get_db

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["Comments"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
def add_comment(post_id: int, comment_data: CommentCreate, session: Session = Depends(get_db)) -> CommentResponse:
    comment_service = CommentService(session=session)
    try:
        return comment_service.add_comment(post_id, comment_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[CommentResponse])
def list_comments(post_id: int, session: Session = Depends(get_db)) -> List[CommentResponse]:
    comment_service = CommentService(session=session)
    try:
        return comment_service.get_comments_by_post(post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
def get_comment(post_id: int, comment_id: int, session: Session = Depends(get_db)) -> CommentResponse:
    comment_service = CommentService(session=session)
    comment = comment_service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

@router.put("/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
def update_comment(post_id: int, comment_id: int, user_id: int, comment_data: CommentUpdate, session: Session = Depends(get_db)) -> CommentResponse:
    comment_service = CommentService(session=session)
    try:
        return comment_service.update_comment(comment_id, user_id, comment_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(post_id: int, comment_id: int, user_id: int, session: Session = Depends(get_db)) -> dict:
    comment_service = CommentService(session=session)
    try:
        comment_service.delete_comment(comment_id, user_id)
        return {"message": f"Comment with ID {comment_id} successfully deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
