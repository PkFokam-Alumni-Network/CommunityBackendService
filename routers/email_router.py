from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy.orm import Session
from core.database import get_db
from services.email_service import EmailService
from core.logging_config import LOGGER

router = APIRouter(prefix="/emails", tags=["Emails"])

class EmailRequest(BaseModel):
    subject: str
    template: str
    sender_name: str
    sender_email: EmailStr
    user_ids: List[int]

class ResetPasswordRequest(BaseModel):
    email: EmailStr

@router.post("/send")
def send_emails(
    payload: EmailRequest,
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

@router.post("/reset-password")
def request_password_reset(
    payload: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not payload.email:
        raise HTTPException(status_code=400, detail="Email is required.")
    email_service = EmailService()
    try:
        background_tasks.add_task(email_service.request_password_reset, db, payload.email)
        return {"message": "Password reset email sent successfully."}
    except Exception as e:
        LOGGER.error(f"Error sending password reset email: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
