from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models.resume_review import ResumeReview
from utils.retry import retry_on_db_error


class ResumeReviewRepository:
    @retry_on_db_error()
    def add_resume_review(self, db: Session, resume_review: ResumeReview) -> ResumeReview:
        try:
            db.add(resume_review)
            db.commit()
            db.refresh(resume_review)
            return resume_review
        except IntegrityError:
            db.rollback()
            raise ValueError("Resume review could not be created due to data constraint violations.")
        except OperationalError as e:
            db.rollback()
            raise ConnectionError("Database connection error: " + str(e))
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while creating resume review: {e}")

    @retry_on_db_error()
    def get_resume_review_by_id(self, db: Session, review_id: int) -> Optional[ResumeReview]:
        return db.query(ResumeReview).filter(ResumeReview.id == review_id).first()

    @retry_on_db_error()
    def get_reviews_by_resume_id(self, db: Session, resume_id: int) -> List[ResumeReview]:
        return (
            db.query(ResumeReview)
            .filter(ResumeReview.resume_id == resume_id)
            .order_by(ResumeReview.reviewed_at.desc())
            .all()
        )

    @retry_on_db_error()
    def get_reviews_by_reviewer_id(self, db: Session, reviewer_id: int) -> List[ResumeReview]:
        return (
            db.query(ResumeReview)
            .filter(ResumeReview.reviewer_id == reviewer_id)
            .order_by(ResumeReview.reviewed_at.desc())
            .all()
        )

    @retry_on_db_error()
    def get_latest_review_by_resume_id(self, db: Session, resume_id: int) -> Optional[ResumeReview]:
        
        return (
            db.query(ResumeReview)
            .filter(ResumeReview.resume_id == resume_id)
            .order_by(ResumeReview.reviewed_at.desc())
            .first()
        )

    @retry_on_db_error()
    def update_resume_review(self, db: Session, resume_review: ResumeReview) -> Optional[ResumeReview]:
        try:
            db.merge(resume_review)
            db.commit()
            db.refresh(resume_review)
            return resume_review
        except IntegrityError:
            db.rollback()
            raise ValueError("Resume review could not be updated due to data constraint violations.")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while updating resume review: {e}")

    @retry_on_db_error()
    def delete_resume_review(self, db: Session, review_id: int) -> None:
        review = self.get_resume_review_by_id(db, review_id)
        if not review:
            raise ValueError("Resume review not found.")

        try:
            db.delete(review)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Unable to delete resume review due to integrity constraints")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while deleting the resume review: {e}")