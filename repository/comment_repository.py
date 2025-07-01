from typing import Optional, List
from sqlalchemy.orm import Session
from models.comment import Comment
from utils.singleton_meta import SingletonMeta

class CommentRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def create_comment(self, comment: Comment) -> Optional[Comment]:
        try:
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            return comment
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error creating comment: {e}")

    def get_comments_by_post(self, post_id: int, limit: int = 10, page: int = 1) -> List[Comment]:
        offset = (page - 1) * limit
        return self.db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).offset(offset).limit(limit).all()

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()
    
    def update_comment(self, updated_comment: Comment) -> Optional[Comment]:
        db_comment = self.get_comment_by_id(updated_comment.id)
        try:
            self.db.merge(updated_comment)
            self.db.commit()
            self.db.refresh(db_comment)
            return db_comment
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error updating comment: {e}")
    
    def delete_comment(self, comment_id: int) -> None:
        comment = self.get_comment_by_id(comment_id)
        try:
            self.db.delete(comment)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error deleting comment: {e}")