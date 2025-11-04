from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy.orm import Session
from core.database import get_db
from services.email_service import EmailService
from core.logging_config import LOGGER

router = APIRouter(prefix="/emails", tags=["Emails"])

class UserEmailRequest(BaseModel):
    subject: str
    template: Optional[str] = None
    sender_name: str
    sender_email: EmailStr
    user_ids: Optional[List[int]] = None

class EmailRequest(BaseModel):
    subject: str
    template: Optional[str] = None
    sender_name: str
    sender_email: EmailStr
    recipients: Optional[List[str]] = None

class ResetPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/send_to_users")
def send_emails_to_users(
    payload: UserEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not payload.user_ids:
        raise HTTPException(status_code=400, detail="user_ids cannot be empty.")

    email_service = EmailService()
    background_tasks.add_task(
        email_service.send_templated_emails_to_users,
        db,
        payload.subject,
        payload.template,
        payload.sender_name,
        payload.sender_email,
        payload.user_ids,
    )

    return {"message": f"Emails are being sent to {len(payload.user_ids)} users."}

@router.post("/send")
def send_email(
    payload: EmailRequest,
):
    email_service = EmailService()
    email_service.send_email(
        payload.subject,
        payload.template,
        payload.sender_name,
        payload.sender_email,
        payload.recipients,
    )

    return {"message": f"Email is being sent to {payload.recipients}."}

@router.post("/reset-password")
def request_password_reset(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    if not payload.email:
        raise HTTPException(status_code=400, detail="Email is required.")
    email_service = EmailService()
    try:
        email_service.request_password_reset(db, payload.email)
        return {"message": "Password reset email sent successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        LOGGER.error(f"Error sending password reset email: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
