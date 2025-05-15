from typing import List, Optional
from sqlalchemy.orm import Session

from models.upvote import Upvote
from repository.upvote_repository import UpvoteRepository
from schemas.upvote_schema import UpvoteCreate

class UpvoteService:
    def __init__(self, session: Session):
        self.upvote_repository = UpvoteRepository(session=session)

    def toggle_upvote_on_post(self, user_id: int, post_id: int) -> Upvote:
        existing_upvote = self.upvote_repository.get_upvote_by_user_and_post(user_id, post_id)
        
        if existing_upvote:
            # If exists, delete (remove upvote)
            self.upvote_repository.delete_upvote(existing_upvote)
            return existing_upvote
        else:
            # If doesn't exist, create new upvote
            new_upvote = Upvote(user_id=user_id, post_id=post_id)
            return self.upvote_repository.create_upvote(new_upvote)

    def count_upvotes(self, post_id: int) -> int:
        return self.upvote_repository.count_upvotes(post_id)

    def check_if_user_upvoted(self, user_id: int, post_id: int) -> bool:
        return self.upvote_repository.get_upvote_by_user_and_post(user_id, post_id) is not None