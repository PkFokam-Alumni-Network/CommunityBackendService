from sqlalchemy.orm import Session

from models.upvote import Upvote
from repository.upvote_repository import UpvoteRepository

class UpvoteService:
    def __init__(self):
        self.upvote_repository = UpvoteRepository()

    def upvote_post(self, post_id: int, user_id: int, db: Session) -> tuple[Upvote, int]:
        existing_upvote = self.upvote_repository.get_upvote_by_user_and_post(db=db, user_id=user_id, post_id=post_id)
        if existing_upvote:
            raise ValueError("You have already upvoted this post")

        upvote = Upvote(user_id=user_id, post_id=post_id)
        created_upvote = self.upvote_repository.create_upvote(db=db, upvote=upvote)
        likes_count = self.get_post_upvote_count(post_id, db)
        return created_upvote, likes_count

    def upvote_comment(self, comment_id: int, user_id: int, db: Session) -> Upvote:
        existing_upvote = self.upvote_repository.get_upvote_by_user_and_comment(db=db, user_id=user_id, comment_id=comment_id)
        if existing_upvote:
            raise ValueError("You have already upvoted this comment")
        
        upvote = Upvote(user_id=user_id, comment_id=comment_id)
        return self.upvote_repository.create_upvote(db=db, upvote=upvote)

    def remove_upvote_from_post(self, post_id: int, user_id: int, db: Session) -> int:
        upvote = self.upvote_repository.get_upvote_by_user_and_post(db=db, user_id=user_id, post_id=post_id)
        if not upvote:
            raise ValueError("Upvote not found")
        self.upvote_repository.delete_upvote(db=db, upvote_id=upvote.id)
        likes_count = self.get_post_upvote_count(post_id, db)
        return likes_count

    def remove_upvote_from_comment(self, comment_id: int, user_id: int, db: Session) -> int:
        upvote = self.upvote_repository.get_upvote_by_user_and_comment(db=db, user_id=user_id, comment_id=comment_id)
        if not upvote:
            raise ValueError("Upvote not found")
        self.upvote_repository.delete_upvote(db=db, upvote_id=upvote.id)

    def get_post_upvote_count(self, post_id: int, db: Session) -> int:
        return self.upvote_repository.get_post_upvote_count(post_id, db)
    
    def get_comment_upvote_count(self, comment_id: int, db: Session) -> int:
        return self.upvote_repository.get_comment_upvote_count(comment_id, db)