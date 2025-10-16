from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.upvote import Upvote
from utils.retry import retry_on_db_error

class UpvoteRepository:
    def __init__(self, session: Session):
        self.db: Session = session

    @retry_on_db_error()
    def create_upvote(self, upvote: Upvote) -> Upvote:
        try:
            self.db.add(upvote)
            self.db.commit()
            self.db.refresh(upvote)
            return upvote
        except IntegrityError:
            self.db.rollback()
            raise ValueError("You have already upvoted this item")
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def get_upvote_by_user_and_post(self, user_id: int, post_id: int) -> Optional[Upvote]:
        return (
            self.db.query(Upvote)
            .filter(Upvote.user_id == user_id, Upvote.post_id == post_id)
            .first()
        )

    @retry_on_db_error()
    def get_upvote_by_user_and_comment(self, user_id: int, comment_id: int) -> Optional[Upvote]:
        return (
            self.db.query(Upvote)
            .filter(Upvote.user_id == user_id, Upvote.comment_id == comment_id)
            .first()
        )

    @retry_on_db_error()
    def delete_upvote(self, upvote_id: int) -> None:
        upvote = self.db.query(Upvote).filter(Upvote.id == upvote_id).first()
        if not upvote:
            raise ValueError("Upvote not found.")
        try:
            self.db.delete(upvote)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete upvote: {e}")
    
    @retry_on_db_error()
    def get_post_upvote_count(self, post_id: int) -> int:
        return self.db.query(Upvote).filter(Upvote.post_id == post_id).count()
    
    @retry_on_db_error()
    def get_comment_upvote_count(self, comment_id: int) -> int:
        return self.db.query(Upvote).filter(Upvote.comment_id == comment_id).count()