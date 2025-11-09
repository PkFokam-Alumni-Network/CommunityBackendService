from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from schemas.post_schema import PostCreate, PostUpdate, PostResponse, PostDeletedResponse
from services.post_service import PostService
from core.database import get_db
from core.logging_config import LOGGER
from core.auth import get_current_user
from models.user import User


router = APIRouter(prefix="/posts", tags=["Posts"])
post_service = PostService()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post_data: PostCreate, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> PostResponse:
    return post_service.add_post(post_data=post_data, user_id=current_user.id, db=session)

@router.get("/recent", status_code=status.HTTP_200_OK, response_model=List[PostResponse])
def get_recent_posts(category: Optional[str] = Query(None, description="Filter by category"), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), session: Session = Depends(get_db)) -> List[PostResponse]:
    if category:
        return post_service.get_recent_posts_by_category(category=category, db=session, limit=limit, page=page)
    return post_service.get_recent_posts(db=session, limit=limit, page=page)

@router.get("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponse)
def get_post(post_id: int, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> PostResponse:
    post = post_service.get_post_by_id(post_id=post_id, user_id=current_user.id, db=session)
    if not post:
        LOGGER.error(f"Post not found: {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.put("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> PostResponse:
    try:
        return post_service.update_post(post_id=post_id, user_id=current_user.id, updated_data=post_data, db=session)
    except ValueError as e:
        LOGGER.error(f"Post not found: {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        LOGGER.error(f"Not authorized to update post: {post_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.delete("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostDeletedResponse)
def delete_post(post_id: int, session: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> PostDeletedResponse:
    try:
        post_service.delete_post(post_id=post_id, user_id=current_user.id, db=session)
        return PostDeletedResponse(message=f"Post with ID {post_id} was successfully deleted")
    except ValueError as e:
        LOGGER.error(f"Post not found: {post_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        LOGGER.error(f"Not authorized to delete post: {post_id}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/user/{user_id}", status_code=status.HTTP_200_OK, response_model=List[PostResponse])
def get_user_posts(user_id: int, session: Session = Depends(get_db)) -> List[PostResponse]:
    return post_service.get_user_posts(user_id=user_id, db=session)
