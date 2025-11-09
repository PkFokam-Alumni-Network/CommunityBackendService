from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError
from models.resume import Resume, ResumeStatus
from utils.retry import retry_on_db_error


class ResumeRepository():
    @retry_on_db_error()
    def add_resume(self, db: Session, resume: Resume) -> Resume:
        try:
            db.add(resume)
            db.commit()
            db.refresh(resume)
            return resume
        except IntegrityError:
            db.rollback()
            raise ValueError("Resume could not be created due to data constraint violations.")
        except OperationalError as e:
            db.rollback()
            raise ConnectionError("Database connection error: " + str(e))
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")
        
    @retry_on_db_error()
    def get_resume_by_id(self, db: Session, resume_id: int) -> Optional[Resume]:
        return db.query(Resume).filter(Resume.id == resume_id).first()
    
    @retry_on_db_error()
    def get_resumes_by_user_id(self, db: Session, user_id: int) -> List[Resume]:
        return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.uploaded_at.desc()).all()
    
    @retry_on_db_error()
    def get_user_resume_by_status(self, db: Session, user_id: int, statuses: List[ResumeStatus]) -> Optional[Resume]:
        
        return (
            db.query(Resume)
            .filter(Resume.user_id == user_id, Resume.status.in_(statuses))
            .first()
        )

    
    @retry_on_db_error()
    def get_resumes_by_status(self, db: Session, status: ResumeStatus, limit: int = 10, page: int = 1) -> List[Resume]:
        offset = (page - 1) * limit
        return (
            db.query(Resume)
            .filter(Resume.status == status)
            .order_by(Resume.uploaded_at.asc())  
            .offset(offset)
            .limit(limit)
            .all()
        )
    @retry_on_db_error()
    def update_resume_status(self, db: Session, resume_id: int, status: ResumeStatus) -> Optional[Resume]:
        
        resume = self.get_resume_by_id(db, resume_id)
        if not resume:
            raise ValueError("Resume not found.")
        
        try:
            resume.status = status
            db.commit()
            db.refresh(resume)
            return resume
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred while updating resume status: {e}")
    
    @retry_on_db_error()
    def update_resume(self, db: Session, resume: Resume) -> Optional[Resume]:
        try:
            db.merge(resume)
            db.commit()
            db.refresh(resume)
            return resume
        except IntegrityError:
            db.rollback()
            raise ValueError("Resume could not be updated due to data constraint violations")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")
        
    @retry_on_db_error()
    def delete_resume(self, db: Session, resume_id: int) -> None:
        resume = self.get_resume_by_id(db, resume_id)
        if not resume:
            raise ValueError("Resume not found.")
        
        try:
            db.delete(resume)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Cannot delete resume due to integrity constraints.")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An error occurred: {e}")
        
    @retry_on_db_error()
    def count_resumes_by_status(self, db: Session, status: ResumeStatus) -> int:
        return db.query(Resume).filter(Resume.status == status).count()