from typing import List, Optional
from sqlalchemy.orm import Session

from models.post import Post
from repository.post_repository import PostRepository
from repository.user_repository import UserRepository
from schemas.post_schema import PostCreate, PostUpdate
from models.enums import AttachmentType
from utils.image_utils import validate_image
from utils.func_utils import upload_image_to_s3
from uuid import uuid4
from core.logging_config import LOGGER

class PostService:
    def __init__(self, session: Session):
        self.post_repository = PostRepository(session=session)
        self.user_repository = UserRepository()

    def add_post(self, post_data: PostCreate, user_id: int) -> Post:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            category=post_data.category,
            author_id=user_id,
            attachment_type=post_data.attachment_type
        )
        post = self.post_repository.create_post(post)
        if post_data.attachment_type == AttachmentType.IMAGE:
            url = self.save_post_attachment(attachment=post_data.attachment, post_id=post.id)
            post.attachment_url = url
        elif post_data.attachment_type == AttachmentType.GIPHY:
            post.attachment_url = post_data.attachment
        self.post_repository.update_post(post)
        return post

    def is_post_exists(self, post_id: int) -> bool:
        return self.post_repository.get_post_by_id(post_id) is not None

    def update_post(self, post_id: int, user_id: int, updated_data: PostUpdate) -> Post:
        db_post = self.post_repository.get_post_by_id(post_id)
        if not db_post:
            raise ValueError("Post not found.")
        if db_post.author_id != user_id:
            raise PermissionError("Not authorized")
        
        if updated_data.attachment_type == AttachmentType.IMAGE:
            url = self.save_post_attachment(attachment=updated_data.attachment, post_id=db_post.id)
            updated_data.attachment = url
        
        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if key == "attachment":
                continue
            if hasattr(db_post, key):
                setattr(db_post, key, value)
        db_post.attachment_url = updated_data.attachment
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

    def save_post_attachment(self, attachment: str, post_id: int) -> str:
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
