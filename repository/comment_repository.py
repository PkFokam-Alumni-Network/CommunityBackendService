from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.comment import Comment
from models.upvote import Upvote
from utils.retry import retry_on_db_error

class CommentRepository:
    def __init__(self, session: Session):
        self.db: Session = session

    @retry_on_db_error()
    def create_comment(self, comment: Comment) -> Comment:
        try:
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            return comment
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    @retry_on_db_error()
    def get_comments_by_post_id(self, post_id: int) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.desc())
            .all()
        )
    
    @retry_on_db_error()
    def get_comments_by_post_id_with_upvote_count(self, post_id: int) -> List[tuple]:
        """Returns list of tuples (Comment, upvote_count)"""
        return (
            self.db.query(Comment, func.count(Upvote.id).label('upvote_count'))
            .outerjoin(Upvote, Upvote.comment_id == Comment.id)
            .filter(Comment.post_id == post_id)
            .group_by(Comment.id)
            .order_by(Comment.created_at.desc())
            .all()
        )

    @retry_on_db_error()
    def update_comment(self, updated_comment: Comment) -> Optional[Comment]:
        db_comment = self.get_comment_by_id(updated_comment.id)
        if not db_comment:
            raise ValueError("Comment not found.")
        try:
            self.db.merge(updated_comment)
            self.db.commit()
            self.db.refresh(db_comment)
            return db_comment
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update comment: {e}")
    
    @retry_on_db_error()
    def delete_comment(self, comment_id: int) -> None:
        db_comment = self.get_comment_by_id(comment_id)
        if not db_comment:
            raise ValueError("Comment not found.")
        try:
            self.db.delete(db_comment)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete comment: {e}")