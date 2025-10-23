from typing import List, Optional
from sqlalchemy.orm import Session

from models.post import Post
from repository.post_repository import PostRepository
from repository.user_repository import UserRepository
from schemas.post_schema import PostCreate, PostUpdate

class PostService:
    def __init__(self, session: Session):
        self.post_repository = PostRepository(session=session)
        self.user_repository = UserRepository()

    def add_post(self, post_data: PostCreate, user_id: int) -> Post:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            category=post_data.category,
            author_id=user_id
        )
        return self.post_repository.create_post(post)

    def is_post_exists(self, post_id: int) -> bool:
        return self.post_repository.get_post_by_id(post_id) is not None

    def update_post(self, post_id: int, user_id: int, updated_data: PostUpdate) -> Post:
        db_post = self.post_repository.get_post_by_id(post_id)
        if not db_post:
            raise ValueError("Post not found.")
        if db_post.author_id != user_id:
            raise PermissionError("Not authorized")
        
        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if hasattr(db_post, key):
                setattr(db_post, key, value)
        return self.post_repository.update_post(db_post)

    def get_post_by_id(self, post_id: int) -> Optional[Post]:
        return self.post_repository.get_post_by_id(post_id)

    def get_recent_posts(self, limit: int = 10, page: int = 1) -> List[Post]:
        return self.post_repository.get_recent_posts(limit=limit, page=page)

    def get_recent_posts_by_category(self, category: str, limit: int = 10, page: int = 1) -> List[Post]:
        return self.post_repository.get_post_by_category(category, limit=limit, page=page)

    def delete_post(self, post_id: int, user_id: int) -> None:
        post = self.post_repository.get_post_by_id(post_id)
        if not post:
            raise ValueError("Post not found.")
        if post.author_id != user_id:
            raise PermissionError("Not authorized")
        self.post_repository.delete_post(post_id)
    
    def get_user_posts(self, user_id: int) -> List[Post]:
        return self.post_repository.get_user_posts(user_id)
