from typing import List, Optional, Type
from sqlalchemy.orm import Session

from models.post import Post
from repository.post_repository import PostRepository
from schemas.post_schema import PostCreate

class PostService:
    def __init__(self, session: Session):
        self.post_repository = PostRepository(session=session)

    def add_post(self, post_data: PostCreate, user_id: int) -> Post:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            category=post_data.category,
            author_id=user_id  # setting user as the author
        )
        return self.post_repository.create_post(post)

    def post_exists(self, post_id: int) -> bool:
        return self.post_repository.get_post_by_id(post_id) is not None
    
    def is_post_owned_by_user(self, post_id: int, user_id: int) -> bool:
        post = self.post_repository.get_post_by_id(post_id)
        return post is not None and post.author_id == user_id

    def update_post(self, post_id: int, user_id: int, updated_data: dict) -> Post:
        db_post = self.post_repository.get_post_by_id(post_id)
        if not db_post:
            raise ValueError("Post not found.")
        if db_post.author_id != user_id:
            raise PermissionError("Not authorized to update this post.")
        
        for key, value in updated_data.items():
            if hasattr(db_post, key):
                setattr(db_post, key, value)
        return self.post_repository.update_post(db_post)

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.post_repository.get_post_by_id(post_id)

    def get_recent_posts(self, limit: int = 10, page: int = 1) -> List[Post]:
        return self.post_repository.get_recent_posts(limit=limit, page=page)

    def get_recent_posts_by_category(self, category: str, limit: int = 10, page: int = 1) -> List[Post]:
        return self.post_repository.get_post_by_category(category, limit=limit, page=page)

    def update_post_title(self, post_id: int, user_id: int, new_title: str) -> Optional[Post]:
        db_post = self.post_repository.get_post_by_id(post_id)
        if not db_post:
            raise ValueError("Post not found.")
        if db_post.author_id != user_id:
            raise PermissionError("Not authorized to update this post.")
        
        db_post.title = new_title
        self.post_repository.update_post(db_post, user_id)
        return db_post
    
    def update_post_category(self, post_id: int, user_id: int, new_category: str) -> Optional[Post]:
        db_post = self.post_repository.get_post_by_id(post_id)
        if not db_post:
            raise ValueError("Post not found.")
        if db_post.author_id != user_id:
            raise PermissionError("Not authorized to update this post.")
        
        db_post.category = new_category
        self.post_repository.update_post(db_post, user_id)
        return db_post

    def delete_post(self, post_id: int, user_id: int) -> None:
        post = self.post_repository.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found.")
        if post.author_id != user_id:
            raise PermissionError("Not authorized to delete this post.")
        self.post_repository.delete_post(post_id, user_id)
