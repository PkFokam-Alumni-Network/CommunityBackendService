from typing import Optional, List
from sqlalchemy.orm import Session
from models.post import Post
from utils.retry import retry_on_db_error
class PostRepository():

    @retry_on_db_error()
    def create_post(self, post: Post, db: Session) -> Post:
        try: 
            db.add(post)
            db.commit()
            db.refresh(post)
            return post
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    @retry_on_db_error()
    def get_post_by_id(self, post_id: int, db: Session) -> Optional[Post]:
        return db.query(Post).filter(Post.id == post_id).first()

    @retry_on_db_error()
    def get_recent_posts(self, db: Session, limit: int = 10, page: int = 1) -> List[Post]:
        offset = (page - 1) * limit
        return (
            db.query(Post)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    @retry_on_db_error()
    def get_post_by_category(self, db: Session, category: str, limit: int = 10, page: int = 1) -> List[Post]:
        offset = (page - 1) * limit
        return (
            db.query(Post)
            .filter(Post.category == category)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    @retry_on_db_error()
    def update_post(self, updated_post: Post, db: Session) -> Optional[Post]:
        db_post = self.get_post_by_id(updated_post.id, db)
        if not db_post:
            raise ValueError("Post not found.")
        try:
            db.merge(updated_post)
            db.commit()
            db.refresh(db_post)
            return db_post
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Failed to update post: {e}")
        
    @retry_on_db_error()
    def delete_post(self, post_id: int, db: Session) -> None:
        db_post = self.get_post_by_id(post_id, db)
        if not db_post:
            raise ValueError("Post not found.")
        try:
            db.delete(db_post)
            db.commit()
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Failed to delete post: {e}")
    
    @retry_on_db_error()
    def get_user_posts(self, user_id: int, db: Session) -> List[Post]:
        return db.query(Post).filter(Post.author_id == user_id).all()

