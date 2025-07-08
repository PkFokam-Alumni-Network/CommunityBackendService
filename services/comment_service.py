from typing import List, Optional
from sqlalchemy.orm import Session

from models.comment import Comment
from services.post_service import PostService
from repository.comment_repository import CommentRepository
from schemas.comment_schema import CommentCreate, CommentUpdate

class CommentService:
    def __init__(self, session: Session):
        self.session = session
        self.comment_repository = CommentRepository(session=session)
        self.post_service = PostService(session=session)
    
    def _validate_post_exists(self, post_id: int):
        if not self.post_service.post_exists(post_id):
            raise ValueError("Post not found.")

    def is_comment_owned_by_user(self, comment_id: int, user_id: int) -> bool:
        comment = self.comment_repository.get_comment_by_id(comment_id)
        return comment is not None and comment.author_id == user_id

    def add_comment(self, comment_data: CommentCreate, post_id: int, user_id: int) -> Comment:
        self._validate_post_exists(post_id)
        comment = Comment(
            content=comment_data.content,
            author_id=user_id,
            post_id=post_id
        )
        return self.comment_repository.create_comment(comment)

    def get_comments_by_post(self, post_id: int, limit: int = 20, page: int = 1) -> List[Comment]:
        self._validate_post_exists(post_id)
        return self.comment_repository.get_comments_by_post(post_id, limit=limit, page=page)

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.comment_repository.get_comment_by_id(comment_id)

    def update_comment(self, comment_id: int, user_id: int, updated_data: CommentUpdate) -> Comment:
        comment = self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
        if comment.author_id != user_id:
            raise PermissionError("Not authorized.")
        if updated_data.content.strip() == "":
            raise ValueError("Content cannot be empty.")

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if hasattr(comment, key):
                setattr(comment, key, value)

        return self.comment_repository.update_comment(comment)

    def delete_comment(self, comment_id: int, user_id: int) -> None:
        comment = self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
        if comment.author_id != user_id:
            raise PermissionError("Not authorized.")
        
        self.comment_repository.delete_comment(comment_id)
