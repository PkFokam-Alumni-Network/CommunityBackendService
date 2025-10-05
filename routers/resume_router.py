from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from services.resume_service import ResumeService
from schemas.resume_schema import (
    ResumeResponse,
    ResumeWithReviews,
    ResumeUploadResponse,
    ResumesForReviewListResponse,
    ResumeReviewCreate,
    ResumeStatusUpdate,
    ResumeDeletedResponse,
    ResumeForReviewResponse
)
from models.resume import ResumeStatus
from core.logging_config import LOGGER

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResumeUploadResponse)
def upload_resume(
    user_id: int = Query(..., description="ID of the user uploading the resume"),
    file: UploadFile = File(..., description="Resume file (PDF only)"),
    db: Session = Depends(get_db)
) -> ResumeUploadResponse:
    """Upload a new resume."""
    resume_service = ResumeService()
    
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed for resume uploads."
            )
        
        file_content = file.file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
        
        resume = resume_service.upload_resume(db, user_id, file_content, file.filename)
        
        LOGGER.info(f"Resume uploaded successfully: user_id={user_id}, resume_id={resume.id}")
        
        return ResumeUploadResponse(
            id=resume.id,
            file_name=resume.file_name,
            status="uploaded",
            message="Resume uploaded successfully."
        )
        
    except ValueError as e:
        LOGGER.warning(f"Resume upload failed for user_id={user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in upload_resume for user_id={user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", status_code=status.HTTP_200_OK, response_model=List[ResumeResponse])
def get_my_resumes(
    user_id: int = Query(..., description="ID of the user"),
    db: Session = Depends(get_db)
) -> List[ResumeResponse]:
    """Get all resumes for the current user."""
    resume_service = ResumeService()
    
    try:
        resumes = resume_service.get_user_resumes(db, user_id)
        return resumes
    except ValueError as e:
        LOGGER.warning(f"Get user resumes failed for user_id={user_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_my_resumes for user_id={user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", status_code=status.HTTP_200_OK, response_model=ResumesForReviewListResponse)
def get_resumes_for_review(
    reviewer_id: int = Query(..., description="ID of the reviewer"),
    status_filter: ResumeStatus = Query(ResumeStatus.pending, alias="status", description="Status of resumes to retrieve"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
) -> ResumesForReviewListResponse:
    """Get resumes available for review (admin only)."""
    resume_service = ResumeService()
    
    try:
        resumes = resume_service.get_resumes_for_review(db, reviewer_id, limit, page)
        total_count = resume_service.resume_repository.count_resumes_by_status(db, status_filter)
        
        resume_responses = []
        for resume in resumes:
            user_name = f"{resume.user.first_name} {resume.user.last_name}" if resume.user else "Unknown"
            resume_responses.append(ResumeForReviewResponse(
                id=resume.id,
                user_id=resume.user_id,
                file_name=resume.file_name,
                uploaded_at=resume.uploaded_at,
                user_name=user_name
            ))
        
        return ResumesForReviewListResponse(
            page_number=page,
            limit=limit,
            total=total_count,
            resumes=resume_responses
        )
        
    except ValueError as e:
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_resumes_for_review for reviewer_id={reviewer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{resume_id}", status_code=status.HTTP_200_OK, response_model=ResumeWithReviews)
def get_resume_by_id(
    resume_id: int,
    user_id: int = Query(..., description="ID of the requesting user"),
    db: Session = Depends(get_db)
) -> ResumeWithReviews:
    """Get a specific resume with its reviews."""
    resume_service = ResumeService()
    
    try:
        resume = resume_service.get_resume_by_id(db, resume_id, user_id)
        reviews = resume_service.get_resume_reviews(db, resume_id, user_id)
        
        return ResumeWithReviews(
            id=resume.id,
            user_id=resume.user_id,
            file_name=resume.file_name,
            file_path=resume.file_path,
            status=resume.status,
            uploaded_at=resume.uploaded_at,
            updated_at=resume.updated_at,
            reviews=reviews
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in get_resume_by_id for resume_id={resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/{resume_id}/review", status_code=status.HTTP_201_CREATED)
def submit_resume_review(
    resume_id: int,
    review_data: ResumeReviewCreate,
    reviewer_id: int = Query(..., description="ID of the reviewer"),
    db: Session = Depends(get_db)
):
    """Submit a review for a resume (admin only)."""
    resume_service = ResumeService()
    
    try:
        review = resume_service.submit_resume_review(
            db, resume_id, reviewer_id, review_data.comments
        )
        
        LOGGER.info(f"Resume review submitted: resume_id={resume_id}, reviewer_id={reviewer_id}")
        
        return {
            "review_id": review.id,
            "status": "review_submitted",
            "message": "Review submitted successfully."
        }
        
    except ValueError as e:
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in submit_resume_review for resume_id={resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{resume_id}/status", status_code=status.HTTP_200_OK, response_model=ResumeResponse)
def update_resume_status(
    resume_id: int,
    status_update: ResumeStatusUpdate,
    user_id: int = Query(..., description="ID of the requesting user"),
    db: Session = Depends(get_db)
) -> ResumeResponse:
    """Update the status of a resume (admin only)."""
    resume_service = ResumeService()
    
    try:
        updated_resume = resume_service.update_resume_status(
            db, resume_id, status_update.status, user_id
        )
        
        LOGGER.info(f"Resume status updated: resume_id={resume_id}, new_status={status_update.status}")
        
        return ResumeResponse(
            id=updated_resume.id,
            user_id=updated_resume.user_id,
            file_name=updated_resume.file_name,
            file_path=updated_resume.file_path,
            status=updated_resume.status,
            uploaded_at=updated_resume.uploaded_at,
            updated_at=updated_resume.updated_at
        )
        
    except ValueError as e:
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in update_resume_status for resume_id={resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK, response_model=ResumeDeletedResponse)
def delete_resume(
    resume_id: int,
    user_id: int = Query(..., description="ID of the requesting user"),
    db: Session = Depends(get_db)
) -> ResumeDeletedResponse:
    """Delete a resume (owner or admin only)."""
    resume_service = ResumeService()
    
    try:
        resume_service.delete_resume(db, resume_id, user_id)
        
        LOGGER.info(f"Resume deleted: resume_id={resume_id}, user_id={user_id}")
        
        return ResumeDeletedResponse(
            message=f"Resume with ID {resume_id} was successfully deleted."
        )
        
    except ValueError as e:
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in delete_resume for resume_id={resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/can-upload", status_code=status.HTTP_200_OK)
def can_upload_resume(
    user_id: int = Query(..., description="ID of the user"),
    db: Session = Depends(get_db)
):
    """Check if a user can upload a new resume."""
    resume_service = ResumeService()
    
    try:
        can_upload = resume_service.can_user_upload_resume(db, user_id)
        
        return {
            "can_upload": can_upload,
            "message": "User can upload a new resume." if can_upload else 
                      "User already has a resume pending or in review."
        }
        
    except Exception as e:
        LOGGER.error(f"SERVER ERROR in can_upload_resume for user_id={user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
