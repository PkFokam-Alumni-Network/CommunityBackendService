from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from typing import List
from models.resume import ResumeStatus


class ResumeCreate(BaseModel):
    file_name: str
    
    model_config = ConfigDict(from_attributes=True)


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_path: str
    status: ResumeStatus
    uploaded_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ResumeWithReviews(ResumeResponse):
    reviews: Optional[List["ResumeReviewResponse"]] = []
    
    model_config = ConfigDict(from_attributes=True)


class ResumeUploadResponse(BaseModel):
    id: int
    file_name: str
    status: str
    message: str
    
    model_config = ConfigDict(from_attributes=True)


class ResumeStatusUpdate(BaseModel):
    status: ResumeStatus
    
    model_config = ConfigDict(from_attributes=True)


class ResumeDeletedResponse(BaseModel):
    message: str
    
    model_config = ConfigDict(from_attributes=True)



class ResumeReviewCreate(BaseModel):
    comments: str
    
    model_config = ConfigDict(from_attributes=True)


class ResumeReviewResponse(BaseModel):
    id: int
    resume_id: int
    reviewer_id: int
    comments: str
    reviewed_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ResumeReviewWithReviewer(ResumeReviewResponse):
    reviewer_name: Optional[str] = None  
    
    model_config = ConfigDict(from_attributes=True)



class ResumeListResponse(BaseModel):
    page_number: int
    limit: int
    total: int
    resumes: List[ResumeResponse]
    
    model_config = ConfigDict(from_attributes=True)


class ResumeForReviewResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    uploaded_at: datetime
    user_name: Optional[str] = None  
    
    model_config = ConfigDict(from_attributes=True)


class ResumesForReviewListResponse(BaseModel):
    page_number: int
    limit: int
    total: int
    resumes: List[ResumeForReviewResponse]
    
    model_config = ConfigDict(from_attributes=True)