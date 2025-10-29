from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.upvote import Upvote
from utils.retry import retry_on_db_error

class UpvoteRepository:

    @retry_on_db_error()
    def create_upvote(self,db: Session, upvote: Upvote) -> Upvote:
        try:
            db.add(upvote)
            db.commit()
            db.refresh(upvote)
            return upvote
        except IntegrityError:
            db.rollback()
            raise ValueError("You have already upvoted this item")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def get_upvote_by_user_and_post(self, user_id: int, post_id: int, db: Session) -> Optional[Upvote]:
        return (
            db.query(Upvote)
            .filter(Upvote.user_id == user_id, Upvote.post_id == post_id)
            .first()
        )

    @retry_on_db_error()
    def get_upvote_by_user_and_comment(self, user_id: int, comment_id: int, db: Session) -> Optional[Upvote]:
        return (
            db.query(Upvote)
            .filter(Upvote.user_id == user_id, Upvote.comment_id == comment_id)
            .first()
        )

    @retry_on_db_error()
    def delete_upvote(self, upvote_id: int, db: Session) -> None:
        upvote = db.query(Upvote).filter(Upvote.id == upvote_id).first()
        if not upvote:
            raise ValueError("Upvote not found.")
        try:
            db.delete(upvote)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Failed to delete upvote: {e}")
    
    @retry_on_db_error()
    def get_post_upvote_count(self, post_id: int, db: Session) -> int:
        return db.query(Upvote).filter(Upvote.post_id == post_id).count()
    
    @retry_on_db_error()
    def get_comment_upvote_count(self, comment_id: int, db: Session) -> int:
        return db.query(Upvote).filter(Upvote.comment_id == comment_id).count()