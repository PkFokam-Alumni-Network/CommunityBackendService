from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas.upvote_schema import UpvoteCreatedResponse, UpvoteDeletedResponse, UpvoteResponse
from services.upvote_service import UpvoteService
from core.database import get_db

router = APIRouter(tags=["Upvotes"])

@router.post("/post/{post_id}/upvote", status_code=status.HTTP_201_CREATED, response_model=UpvoteCreatedResponse)
def upvote_post(
    post_id: int,
    user_id: int,
    session: Session = Depends(get_db)
) -> UpvoteCreatedResponse:
    upvote_service = UpvoteService(session=session)
    try:
        upvote = upvote_service.upvote_post(post_id, user_id)
        return UpvoteCreatedResponse(
            message="Post upvoted successfully",
            upvote=UpvoteResponse.model_validate(upvote)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/post/{post_id}/upvote", status_code=status.HTTP_200_OK, response_model=UpvoteDeletedResponse)
def remove_upvote_from_post(
    post_id: int,
    user_id: int,
    session: Session = Depends(get_db)
) -> UpvoteDeletedResponse:
    upvote_service = UpvoteService(session=session)
    try:
        upvote_service.remove_upvote_from_post(post_id, user_id)
        return UpvoteDeletedResponse(message="Upvote removed successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/comment/{comment_id}/upvote", status_code=status.HTTP_201_CREATED, response_model=UpvoteCreatedResponse)
def upvote_comment(
    comment_id: int,
    user_id: int,
    session: Session = Depends(get_db)
) -> UpvoteCreatedResponse:
    upvote_service = UpvoteService(session=session)
    try:
        upvote = upvote_service.upvote_comment(comment_id, user_id)
        return UpvoteCreatedResponse(
            message="Comment upvoted successfully",
            upvote=UpvoteResponse.model_validate(upvote)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/comment/{comment_id}/upvote", status_code=status.HTTP_200_OK, response_model=UpvoteDeletedResponse)
def remove_upvote_from_comment(
    comment_id: int,
    user_id: int,
    session: Session = Depends(get_db)
) -> UpvoteDeletedResponse:
    upvote_service = UpvoteService(session=session)
    try:
        upvote_service.remove_upvote_from_comment(comment_id, user_id)
        return UpvoteDeletedResponse(message="Upvote removed successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))