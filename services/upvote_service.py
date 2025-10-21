from sqlalchemy.orm import Session

from models.upvote import Upvote
from repository.upvote_repository import UpvoteRepository

class UpvoteService:
    def __init__(self, session: Session):
        self.upvote_repository = UpvoteRepository(session=session)

    def upvote_post(self, post_id: int, user_id: int) -> Upvote:
        existing_upvote = self.upvote_repository.get_upvote_by_user_and_post(user_id, post_id)
        if existing_upvote:
            raise ValueError("You have already upvoted this post")
        
        upvote = Upvote(user_id=user_id, post_id=post_id)
        return self.upvote_repository.create_upvote(upvote)

    def upvote_comment(self, comment_id: int, user_id: int) -> Upvote:
        existing_upvote = self.upvote_repository.get_upvote_by_user_and_comment(user_id, comment_id)
        if existing_upvote:
            raise ValueError("You have already upvoted this comment")
        
        upvote = Upvote(user_id=user_id, comment_id=comment_id)
        return self.upvote_repository.create_upvote(upvote)

    def remove_upvote_from_post(self, post_id: int, user_id: int) -> None:
        upvote = self.upvote_repository.get_upvote_by_user_and_post(user_id, post_id)
        if not upvote:
            raise ValueError("Upvote not found")
        self.upvote_repository.delete_upvote(upvote.id)

    def remove_upvote_from_comment(self, comment_id: int, user_id: int) -> None:
        upvote = self.upvote_repository.get_upvote_by_user_and_comment(user_id, comment_id)
        if not upvote:
            raise ValueError("Upvote not found")
        self.upvote_repository.delete_upvote(upvote.id)

    def get_post_upvote_count(self, post_id: int) -> int:
        return self.upvote_repository.get_post_upvote_count(post_id)
    
    def get_comment_upvote_count(self, comment_id: int) -> int:
        return self.upvote_repository.get_comment_upvote_count(comment_id)