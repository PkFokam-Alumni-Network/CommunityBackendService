from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session

from models.comment import Comment
from repository.comment_repository import CommentRepository
from schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse
from models.enums import AttachmentType
from utils.image_utils import validate_image
from utils.func_utils import upload_image_to_s3
from core.logging_config import LOGGER

class CommentService:
    def __init__(self, session: Session):
        self.comment_repository = CommentRepository(session=session)

    def add_comment(self, post_id: int, comment_data: CommentCreate, user_id: int) -> Comment:
        url = None
        if comment_data.attachment_type == AttachmentType.IMAGE:
            url = self.save_comment_attachment(post_id=post_id, attachment=comment_data.attachment)
        elif comment_data.attachment_type == AttachmentType.GIPHY:
            url = comment_data.attachment
        comment = Comment(
            post_id=post_id,
            content=comment_data.content,
            author_id=user_id,
            attachment_url=url,
            attachment_type=comment_data.attachment_type
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

        if updated_data.attachment_type == AttachmentType.IMAGE:
            url = self.save_comment_attachment(post_id=db_comment.post_id, attachment=updated_data.attachment)
            updated_data.attachment = url

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            # skip raw attachment data
            if key == "attachment":
               continue
            if hasattr(db_comment, key):
                setattr(db_comment, key, value)
        
        db_comment.attachment_url = updated_data.attachment
        return self.comment_repository.update_comment(db_comment)

    def delete_comment(self, comment_id: int, user_id: int) -> None:
        comment = self.comment_repository.get_comment_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
        if comment.author_id != user_id:
            raise PermissionError("Not authorized")
        self.comment_repository.delete_comment(comment_id)
    
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