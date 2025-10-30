from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from models.comment import Comment
from repository.comment_repository import CommentRepository
from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse, Author
from models.enums import AttachmentType
from utils.image_utils import validate_image
from utils.func_utils import upload_image_to_s3
from core.logging_config import LOGGER
from repository.user_repository import UserRepository

class CommentService:
    def __init__(self):
        self.comment_repository = CommentRepository()
        self.user_repository = UserRepository()

    def _create_author(self, user_id: int, db: Session) -> Author:
        user = self.user_repository.get_user_by_id(user_id=user_id, db=db)
        return Author(
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.image
        )

    def _create_comment_response(self, comment: Comment, author: Author, upvote_count: Optional[int] = 0) -> CommentResponse:
        comment_response = CommentResponse.model_validate(comment, from_attributes=True).model_copy(update={"author": author})
        comment_response.upvote_count = upvote_count
        return comment_response

    def _verify_comment_ownership(self, comment: Comment, user_id: int) -> None:
        if not comment:
            raise ValueError("Comment not found.")
        if comment.author_id != user_id:
            raise PermissionError("Not authorized")

    def _handle_attachment(self, attachment_type: AttachmentType, attachment: str, post_id: int) -> Optional[str]:
        if attachment_type == AttachmentType.IMAGE:
            return self.save_comment_attachment(post_id=post_id, attachment=attachment)
        elif attachment_type == AttachmentType.GIPHY:
            return attachment
        return None

    def add_comment(self, db: Session, post_id: int, comment_data: CommentCreate, user_id: int) -> CommentResponse:
        url = self._handle_attachment(
            comment_data.attachment_type,
            comment_data.attachment,
            post_id
        )
        
        comment = Comment(
            post_id=post_id,
            content=comment_data.content,
            author_id=user_id,
            attachment_url=url,
            attachment_type=comment_data.attachment_type
        )
        comment = self.comment_repository.create_comment(db=db, comment=comment)
        
        author = self._create_author(user_id, db)
        return self._create_comment_response(comment, author)

    def get_comment_by_id(self, db: Session, comment_id: int) -> Optional[CommentResponse]:
        comment = self.comment_repository.get_comment_by_id(db=db, comment_id=comment_id)
        if not comment:
            return None
        
        author = self._create_author(comment.author_id, db)
        return self._create_comment_response(comment, author)

    def get_comments_by_post_id(self, db: Session, post_id: int) -> List[CommentResponse]:
        comment_tuples = self.comment_repository.get_comments_by_post_id_with_upvote_count(post_id)
        
        result = []
        for comment, upvote_count in comment_tuples:
            author = self._create_author(comment.author_id, db)
            comment_response = self._create_comment_response(comment, author, upvote_count)
            result.append(comment_response)
        
        return result

    def update_comment(self, db: Session, comment_id: int, user_id: int, updated_data: CommentUpdate) -> CommentResponse:
        db_comment = self.comment_repository.get_comment_by_id(db=db, comment_id=comment_id)
        self._verify_comment_ownership(db_comment, user_id)

        attachment_url = updated_data.attachment
        if updated_data.attachment_type == AttachmentType.IMAGE:
            attachment_url = self.save_comment_attachment(
                post_id=db_comment.post_id,
                attachment=updated_data.attachment
            )

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if key != "attachment" and hasattr(db_comment, key):
                setattr(db_comment, key, value)
        
        db_comment.attachment_url = attachment_url
        updated_comment = self.comment_repository.update_comment(db_comment, db)
        
        author = self._create_author(updated_comment.author_id, db)
        return self._create_comment_response(updated_comment, author)

    def delete_comment(self, db: Session, comment_id: int, user_id: int) -> None:
        comment = self.comment_repository.get_comment_by_id(db=db, comment_id=comment_id)
        self._verify_comment_ownership(comment, user_id)
        self.comment_repository.delete_comment(db=db, comment_id=comment_id)
    
    def save_comment_attachment(self, post_id: int, attachment: str) -> str:
        try:
            _ = validate_image(attachment)
            uuid = uuid4()
            file_name = f"posts/{post_id}/comments/{uuid}.png"
            path = upload_image_to_s3(attachment, file_name)
            return path
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            LOGGER.error("Error saving image attachment. ", e)
            raise e