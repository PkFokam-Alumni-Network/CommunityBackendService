from typing import List, Optional
from sqlalchemy.orm import Session

from models.upvote import Upvote
from services.post_service import PostService
from repository.upvote_repository import UpvoteRepository
from schemas.upvote_schema import UpvoteCreate

class UpvoteService:
    def __init__(self, session: Session):
        self.upvote_repository = UpvoteRepository(session=session)

    def _validate_post_exists(self, post_id: int):
        self.post_service = PostService(session=Session)
        if not self.post_service.post_exists(post_id):
            raise ValueError("Post not found.")

    def toggle_upvote_on_post(self, user_id: int, post_id: int) -> tuple[Optional[Upvote], str]:
        self._validate_post_exists(post_id)
        existing_upvote = self.upvote_repository.get_upvote_by_user_and_post(user_id, post_id)
        
        if existing_upvote:
            # If exists, delete (remove upvote)
            self.upvote_repository.delete_upvote(existing_upvote)
            return (None, "removed")
        else:
            # If doesn't exist, create new upvote
            new_upvote = Upvote(user_id=user_id, post_id=post_id)
            upvote = self.upvote_repository.create_upvote(new_upvote)
            return (upvote, "added")

    def count_upvotes(self, post_id: int) -> int:
        self._validate_post_exists(post_id)
        return self.upvote_repository.count_upvotes(post_id)

    def check_if_user_upvoted(self, user_id: int, post_id: int) -> bool:
        self._validate_post_exists(post_id)
        return self.upvote_repository.get_upvote_by_user_and_post(user_id, post_id) is not None