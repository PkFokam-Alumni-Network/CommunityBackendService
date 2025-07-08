from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, CommentDeletedResponse
from services.comment_service import CommentService
from database import get_db

router = APIRouter()

@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
def add_comment(comment_data: CommentCreate, post_id: int, user_id: int, session: Session = Depends(get_db)) -> CommentResponse:
    comment_service = CommentService(session=session)
    try:
        return comment_service.add_comment(comment_data, post_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/posts/{post_id}/comments", status_code=status.HTTP_200_OK, response_model=List[CommentResponse])
def get_comments(post_id: int, session: Session = Depends(get_db)) -> List[CommentResponse]:
    comment_service = CommentService(session=session)
    try:
        return comment_service.get_comments_by_post(post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
def get_comment(comment_id: int, session: Session = Depends(get_db)) -> CommentResponse:
    comment_service = CommentService(session=session)
    comment = comment_service.get_comment_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
    return comment

@router.put("/comments/{comment_id}", status_code=status.HTTP_200_OK, response_model=CommentResponse)
def update_comment(comment_id: int, user_id: int, comment_data: CommentUpdate, session: Session = Depends(get_db)) -> CommentResponse:
    comment_service = CommentService(session=session)
    try:
        return comment_service.update_comment(comment_id, user_id, comment_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(comment_id: int, user_id: int, session: Session = Depends(get_db)) -> dict:
    comment_service = CommentService(session=session)
    try:
        comment_service.delete_comment(comment_id, user_id)
        return {"message": f"Comment with ID {comment_id} successfully deleted."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
