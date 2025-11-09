from typing import List, Optional, Dict
from sqlalchemy.orm import Session

from models.post import Post
from repository.post_repository import PostRepository
from repository.user_repository import UserRepository
from schemas.post_schema import PostCreate, PostUpdate, Author, PostResponse
from models.enums import AttachmentType
from utils.image_utils import validate_image
from utils.func_utils import upload_image_to_s3
from uuid import uuid4
from core.logging_config import LOGGER

class PostService:
    def __init__(self):
        self.post_repository = PostRepository()
        self.user_repository = UserRepository()

    def _create_author(self, user_id: int, db: Session) -> Author:
        user = self.user_repository.get_user_by_id(db=db, user_id=user_id)
        return Author(
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user.image
        )

    def _create_post_response(self, post: Post, author: Author, user_id: Optional[int], db: Session) -> PostResponse:
        likes_count = self.post_repository.count_post_likes(db, post.id)
        comments_count = self.post_repository.count_post_comments(db, post.id)
        liked_by_user = False
        if user_id:
            liked_by_user = self.post_repository.user_has_liked_post(db, post.id, user_id)

        return PostResponse.model_validate(post, from_attributes=True).model_copy(
            update={
                "author": author,
                "likes_count": likes_count,
                "comments_count": comments_count,
                "liked_by_user": liked_by_user
            }
        )

    def _create_post_responses(self, posts: List[Post], user_id: Optional[int], db: Session) -> List[PostResponse]:
        if not posts:
            return []
        
        author_ids = [post.author_id for post in posts]
        authors = self.user_repository.get_users_by_ids(db=db, user_ids=author_ids)
        authors_dict: Dict[int, Author] = {
            author.id: Author(
                first_name=author.first_name,
                last_name=author.last_name,
                avatar_url=author.image
            )
            for author in authors
        }
        post_ids = [post.id for post in posts]
        upvote_counts = self.post_repository.count_post_likes(post_ids, db)
        comment_counts = self.post_repository.count_post_comments(post_ids, db)
        liked_by_user = False
        if user_id:
            liked_by_user = self.post_repository.user_has_liked_post(db, post_ids, user_id)

        return [
            PostResponse.model_validate(post, from_attributes=True).model_copy(
                update={
                    "author": authors_dict[post.author_id],
                    "upvote_count": upvote_counts.get(post.id, 0),
                    "comment_count": comment_counts.get(post.id, 0),
                    "liked_by_user": liked_by_user.get(post.id, False)
                }
            )
            for post in posts
        ]

    def _verify_post_ownership(self, post: Post, user_id: int) -> None:
        if not post:
            raise ValueError("Post not found.")
        if post.author_id != user_id:
            raise PermissionError("Not authorized")

    def _handle_attachment(self, attachment_type: AttachmentType, attachment: str, post_id: int) -> Optional[str]:
        if attachment_type == AttachmentType.IMAGE:
            return self.save_post_attachment(attachment=attachment, post_id=post_id)
        elif attachment_type == AttachmentType.GIPHY:
            return attachment

    def add_post(self, post_data: PostCreate, user_id: int, db: Session) -> PostResponse:
        post = Post(
            title=post_data.title,
            content=post_data.content,
            category=post_data.category,
            author_id=user_id,
            attachment_type=post_data.attachment_type
        )
        post = self.post_repository.create_post(post, db)
        
        attachment_url = self._handle_attachment(
            post_data.attachment_type, 
            post_data.attachment, 
            post.id
        )
        if attachment_url:
            post.attachment_url = attachment_url
            self.post_repository.update_post(post, db)
        
        author = self._create_author(user_id, db)
        return self._create_post_response(post, author, user_id, db)

    def update_post(self, post_id: int, user_id: int, updated_data: PostUpdate, db: Session) -> PostResponse:
        db_post = self.post_repository.get_post_by_id(post_id, db=db)
        self._verify_post_ownership(db_post, user_id)
        
        attachment_url = updated_data.attachment
        if updated_data.attachment_type == AttachmentType.IMAGE:
            attachment_url = self.save_post_attachment(
                attachment=updated_data.attachment, 
                post_id=db_post.id
            )
        
        for key, value in updated_data.model_dump(exclude_unset=True).items():
            if key != "attachment" and hasattr(db_post, key):
                setattr(db_post, key, value)
        
        db_post.attachment_url = attachment_url
        updated_post = self.post_repository.update_post(db_post, db)
        
        author = self._create_author(user_id, db)
        return self._create_post_response(updated_post, author, user_id, db)

    def get_post_by_id(self, post_id: int, user_id: Optional[int], db: Session) -> Optional[PostResponse]:
        post = self.post_repository.get_post_by_id(post_id, db=db)
        if not post:
            return None
        
        author = self._create_author(post.author_id, db)
        return self._create_post_response(post, author, user_id, db)

    def get_recent_posts(self, user_id: Optional[int], db: Session, limit: int = 10, page: int = 1) -> List[PostResponse]:
        posts = self.post_repository.get_recent_posts(limit=limit, page=page, db=db)
        return self._create_post_responses(posts, user_id, db)

    def get_recent_posts_by_category(self, category: str, user_id: Optional[int], db: Session, limit: int = 10, page: int = 1) -> List[PostResponse]:
        posts = self.post_repository.get_post_by_category(category=category, limit=limit, page=page, db=db)
        return self._create_post_responses(posts, user_id, db)

    def delete_post(self, post_id: int, user_id: int, db: Session) -> None:
        post = self.post_repository.get_post_by_id(post_id, db)
        self._verify_post_ownership(post, user_id)
        self.post_repository.delete_post(post_id, db)
    
    def get_user_posts(self, user_id: int, db: Session) -> List[PostResponse]:
        posts = self.post_repository.get_user_posts(user_id, db)
        return self._create_post_responses(posts, user_id, db)

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