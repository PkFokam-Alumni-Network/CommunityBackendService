from typing import List, Optional
from sqlalchemy.orm import Session

from models.comment import Comment
from repository.comment_repository import CommentRepository
from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse

class CommentService:
    def __init__(self, session: Session):
        self.comment_repository = CommentRepository(session=session)

    def add_comment(self, post_id: int, comment_data: CommentCreate, user_id: int) -> Comment:
        comment = Comment(
            post_id=post_id,
            content=comment_data.content,
            author_id=user_id
        )
        return self.comment_repository.create_comment(comment)

    def get_comment_by_id(self, comment_id: int) -> Optional[Comment]:
        return self.comment_repository.get_comment_by_id(comment_id)

    def get_comments_by_post_id(self, post_id: int) -> List[CommentResponse]:
        comment_tuples = self.comment_repository.get_comments_by_post_id_with_upvote_count(post_id)
        
        result = []
        for comment, upvote_count in comment_tuples:
            comment_response = CommentResponse.model_validate(comment)
            comment_response.upvote_count = upvote_count
            result.append(comment_response)
        
        return result

    def update_comment(self, comment_id: int, user_id: int, updated_data: CommentUpdate) -> Comment:
        db_comment = self.comment_repository.get_comment_by_id(comment_id)
        if not db_comment:
            raise ValueError("Comment not found.")
        if db_comment.author_id != user_id:
            raise PermissionError("Not authorized")

        db_comment.content = updated_data.content
        return self.comment_repository.update_comment(db_comment)

    def delete_comment(self, comment_id: int, user_id: int) -> None:
        comment = self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
        if comment.author_id != user_id:
            raise PermissionError("Not authorized")
        self.comment_repository.delete_comment(comment_id)