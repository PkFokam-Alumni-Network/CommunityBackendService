from typing import Optional, List
from sqlalchemy.orm import Session
from models.comment import Comment

class CommentRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def create_comment(self, comment: Comment, user_id: int) -> Optional[Comment]:
        comment.author_id = user_id
        try:
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            return comment
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error creating comment: {e}")

    def get_comments_by_post(self, post_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()
    
    def update_comment(self, updated_comment: Comment, user_id: int) -> Optional[Comment]:
        db_comment = self.get_comment_by_id(updated_comment.id)
        if not db_comment:
            raise ValueError("Comment not found.")
        if db_comment.author_id != user_id:
            raise PermissionError("You are not the author of this comment.")
        try:
            db_comment.content = updated_comment.content
            self.db.commit()
            self.db.refresh(db_comment)
            return db_comment
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error updating comment: {e}")
    
    def delete_comment(self, comment_id: int, user_id: int) -> None:
        comment = self.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
        if comment.author_id != user_id:
            raise PermissionError("You are not authorized to delete this comment.")
        try:
            self.db.delete(comment)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error deleting comment: {e}")