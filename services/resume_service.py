from typing import List, Optional
from sqlalchemy.orm import Session
from models.resume import Resume, ResumeStatus
from models.resume_review import ResumeReview
from repository.resume_repository import ResumeRepository
from repository.resume_review_repository import ResumeReviewRepository
from repository.user_repository import UserRepository
from utils.func_utils import upload_file_to_s3, validate_resume_file
from datetime import datetime
from models.user import UserRole
import uuid
import os


class ResumeService:
    def __init__(self):
        self.resume_repository = ResumeRepository()
        self.resume_review_repository = ResumeReviewRepository()
        self.user_repository = UserRepository()

    def upload_resume(self, db: Session, user_id: int, file_data: bytes, file_name: str) -> Resume:
        """Upload a new resume for a user."""
        
        if not user_id or not file_data or not file_name:
            raise ValueError("User ID, file data, and file name are required.")

        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found.")
        validate_resume_file(file_data, file_name)

        # Check one-resume rule
        existing_resume = self.resume_repository.get_user_resume_by_status(
            db, user_id, [ResumeStatus.pending, ResumeStatus.in_review]
        )
        if existing_resume:
            raise ValueError("You can only have one resume with a status of 'Pending' or 'In Review' at a time.")
        
        try:
            first_name = user.first_name.lower().replace(" ", "_") if user.first_name else "user"
            last_name = user.last_name.lower().replace(" ", "_") if user.last_name else ""
            
            if last_name:
                user_folder = f"{user_id}_{first_name}_{last_name}"
            else:
                user_folder = f"{user_id}_{first_name}"
            
            file_extension = os.path.splitext(file_name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            object_key = f"resumes/{user_folder}/{unique_filename}"
            
            s3_path = upload_file_to_s3(file_data, object_key)
            
            resume = Resume(
                user_id=user_id,
                file_name=file_name,
                file_path=s3_path,
                status=ResumeStatus.pending
            )
            
            return self.resume_repository.add_resume(db, resume)
            
        except Exception as e:
            raise RuntimeError(f"Failed to upload resume: {str(e)}")

    def get_user_resumes(self, db: Session, user_id: int) -> List[Resume]:
        if not user_id:
            raise ValueError("User ID is required.")
        
        user = self.user_repository.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found.")
        
        return self.resume_repository.get_resumes_by_user_id(db, user_id)

    def get_resume_by_id(self, db: Session, resume_id: int, requesting_user_id: int) -> Optional[Resume]:
        if not resume_id or not requesting_user_id:
            raise ValueError("Resume ID and requesting user ID are required.")
        
        resume = self.resume_repository.get_resume_by_id(db, resume_id)
        if not resume:
            raise ValueError("Resume not found.")
        
        if resume.user_id == requesting_user_id:
            return resume
        
        requesting_user = self.user_repository.get_user_by_id(db, requesting_user_id)
        if requesting_user and requesting_user.role == UserRole.admin:
            return resume
        
        raise ValueError("You are not authorized to view this resume.")

    def get_resumes_for_review(self, db: Session, reviewer_id: int, limit: int = 10, page: int = 1) -> List[Resume]:
        if not reviewer_id:
            raise ValueError("Reviewer ID is required.")
        
        reviewer = self.user_repository.get_user_by_id(db, reviewer_id)
        if not reviewer or reviewer.role != UserRole.admin:
            raise ValueError("You are not authorized to review resumes.")
        
        return self.resume_repository.get_resumes_by_status(db, ResumeStatus.pending, limit, page)

    def submit_resume_review(self, db: Session, resume_id: int, reviewer_id: int, comments: str) -> ResumeReview:
        if not resume_id or not reviewer_id or not comments.strip():
            raise ValueError("Resume ID, reviewer ID, and comments are required.")
        
        reviewer = self.user_repository.get_user_by_id(db, reviewer_id)
        if not reviewer or reviewer.role != UserRole.admin:
            raise ValueError("You are not authorized to review resumes.")
        
        resume = self.resume_repository.get_resume_by_id(db, resume_id)
        if not resume:
            raise ValueError("Resume not found.")
        
        if resume.status not in [ResumeStatus.pending, ResumeStatus.in_review]:
            raise ValueError("This resume is not available for review.")
        
        try:
            resume_review = ResumeReview(
                resume_id=resume_id,
                reviewer_id=reviewer_id,
                comments=comments.strip()
            )
            
            review = self.resume_review_repository.add_resume_review(db, resume_review)
            
            self.resume_repository.update_resume_status(db, resume_id, ResumeStatus.reviewed)
            
            return review
            
        except Exception as e:
            raise RuntimeError(f"Failed to submit review: {str(e)}")

    def update_resume_status(self, db: Session, resume_id: int, new_status: ResumeStatus, requesting_user_id: int) -> Resume:
        if not resume_id or not new_status or not requesting_user_id:
            raise ValueError("Resume ID, new status, and requesting user ID are required.")
        
        requesting_user = self.user_repository.get_user_by_id(db, requesting_user_id)
        if not requesting_user or requesting_user.role != UserRole.admin:
            raise ValueError("You are not authorized to update resume status.")
        
        return self.resume_repository.update_resume_status(db, resume_id, new_status)

    def get_resume_reviews(self, db: Session, resume_id: int, requesting_user_id: int) -> List[ResumeReview]:
        if not resume_id or not requesting_user_id:
            raise ValueError("Resume ID and requesting user ID are required.")
        
        resume = self.get_resume_by_id(db, resume_id, requesting_user_id)
        if not resume:
            raise ValueError("Resume not found or access denied.")
        
        return self.resume_review_repository.get_reviews_by_resume_id(db, resume_id)

    def can_user_upload_resume(self, db: Session, user_id: int) -> bool:
        if not user_id:
            return False
        
        existing_resume = self.resume_repository.get_user_resume_by_status(
            db, user_id, [ResumeStatus.pending, ResumeStatus.in_review]
        )
        
        return existing_resume is None

    def delete_resume(self, db: Session, resume_id: int, requesting_user_id: int) -> None:
        if not resume_id or not requesting_user_id:
            raise ValueError("Resume ID and requesting user ID are required.")
        
        resume = self.resume_repository.get_resume_by_id(db, resume_id)
        if not resume:
            raise ValueError("Resume not found.")
        
        requesting_user = self.user_repository.get_user_by_id(db, requesting_user_id)
        if not requesting_user:
            raise ValueError("Requesting user not found.")
        
        if resume.user_id != requesting_user_id and requesting_user.role != UserRole.admin:
            raise ValueError("You are not authorized to delete this resume.")
        
        if resume.status == ResumeStatus.in_review:
            raise ValueError("Cannot delete a resume that is currently being reviewed.")
        
        self.resume_repository.delete_resume(db, resume_id)