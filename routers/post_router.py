from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional

from schemas.post_schema import PostCreate, PostUpdate, PostResponse, PostDeletedResponse
from services.post_service import PostService
from core.database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_post(post_data: PostCreate, user_id: int, session: Session = Depends(get_db)) -> PostResponse:
    post_service = PostService(session=session)
    return post_service.add_post(post_data, user_id)

@router.get("/recent", status_code=status.HTTP_200_OK, response_model=List[PostResponse])
def get_recent_posts(category: Optional[str] = Query(None, description="Filter by category"), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100), session: Session = Depends(get_db)) -> List[PostResponse]:
    post_service = PostService(session=session) 
    
    if category:
        return post_service.get_recent_posts_by_category(category, limit, page)
    return post_service.get_recent_posts(limit, page)

@router.get("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponse)
def get_post(post_id: int, session: Session = Depends(get_db)) -> PostResponse:
    post_service = PostService(session=session)
    post = post_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post

@router.put("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostResponse)
def update_post(post_id: int, user_id: int, post_data: PostUpdate, session: Session = Depends(get_db)) -> PostResponse:
    post_service = PostService(session=session)
    try:
        return post_service.update_post(post_id, user_id, post_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.delete("/{post_id}", status_code=status.HTTP_200_OK, response_model=PostDeletedResponse)
def delete_post(post_id: int, user_id: int, session: Session = Depends(get_db)) -> PostDeletedResponse:
    post_service = PostService(session=session)
    try:
        post_service.delete_post(post_id, user_id)
        return PostDeletedResponse(message=f"Post with ID {post_id} was successfully deleted")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
