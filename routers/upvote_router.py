from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.upvote_schema import UpvoteCreate, UpvoteToggleResponse, UpvoteCountResponse
from services.upvote_service import UpvoteService

router = APIRouter(prefix="/posts/{post_id}/upvotes", tags=["Upvotes"])

@router.post("/", status_code=status.HTTP_200_OK)
def toggle_upvote(post_id: int, upvote_data: UpvoteCreate, session: Session = Depends(get_db)) -> UpvoteToggleResponse:
    upvote_service = UpvoteService(session=session)
    try:
        _, action = upvote_service.toggle_upvote_on_post(upvote_data.user_id, post_id)
        return UpvoteToggleResponse(user_id=upvote_data.user_id, post_id=post_id, action=action)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 

@router.get("/", status_code=status.HTTP_200_OK)
def get_upvote_count(post_id: int, session: Session = Depends(get_db)) -> UpvoteCountResponse:
    upvote_service = UpvoteService(session=session)
    try: 
        count = upvote_service.count_upvotes(post_id)
        return UpvoteCountResponse(post_id=post_id, upvotes=count)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/check", status_code=status.HTTP_200_OK)
def check_user_upvoted(post_id: int, user_id: int, session: Session = Depends(get_db)) -> dict:
    upvote_service = UpvoteService(session=session)
    try:
        has_upvoted = upvote_service.check_if_user_upvoted(user_id, post_id)
        return {"post_id": post_id, "user_id": user_id, "has_upvoted": has_upvoted}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
