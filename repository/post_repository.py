from typing import Optional, List
from sqlalchemy.orm import Session
from models.post import Post
class PostRepository():
    def __init__(self, session: Session):
        self.db: Session = session

    def create_post(self, post: Post) -> Post:
        try: 
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            return post
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"An error occurred: {e}")

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.db.query(Post).filter(Post.id == post_id).first()

    def get_recent_posts(self, limit: int = 10, page: int = 1) -> List[Post]:
        offset = (page - 1) * limit
        return (
            self.db.query(Post)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def get_post_by_category(self, category: str, limit: int = 10, page: int = 1) -> List[Post]:
        offset = (page - 1) * limit
        return (
            self.db.query(Post)
            .filter(Post.category == category)
            .order_by(Post.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
    
    def update_post(self, updated_post: Post) -> Optional[Post]:
        db_post = self.get_post_by_id(updated_post.id)
        if not db_post:
            raise ValueError("Post not found.")
        try:
            self.db.merge(updated_post)
            self.db.commit()
            self.db.refresh(db_post)
            return db_post
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update post: {e}")
        
    def delete_post(self, post_id: int) -> None:
        db_post = self.get_post_by_id(post_id)
        if not db_post:
            raise ValueError("Post not found.")
        try:
            self.db.delete(db_post)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete post: {e}")

