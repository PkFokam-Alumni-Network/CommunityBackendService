from typing import List
import os
from brevo_python import ApiClient, Configuration, SendSmtpEmail
from brevo_python.api.transactional_emails_api import TransactionalEmailsApi
from brevo_python.rest import ApiException
from core.logging_config import LOGGER
from .user_service import UserService
from sqlalchemy.orm import Session
from core.settings import settings
from utils.func_utils import create_jwt

class EmailService:
    def __init__(self):
        config = Configuration()
        config.api_key['api-key'] = os.getenv("BREVO_API_KEY")
        self.api_client = ApiClient(config)
        self.email_api = TransactionalEmailsApi(self.api_client)
        self.user_service = UserService()

    def send_email(
        self,
        subject: str,
        html_content: str,
        sender_name: str,
        sender_email: str,
        recipients: List[str],
    ):
        send_smtp_email = SendSmtpEmail(
            to=[{"email": email} for email in recipients],
            sender={"name": sender_name, "email": sender_email},
            subject=subject,
            html_content=html_content,
        )
        try:
            self.email_api.send_transac_email(send_smtp_email)
        except ApiException as e:
            LOGGER.error("Failed to send email: %s", e)
            raise e

    def send_templated_emails_to_users(
        self,
        db: Session,
        subject: str,
        template: str,
        sender_name: str,
        sender_email: str,
        user_ids: List[int],
    ):
        users = self.user_service.get_users_by_ids(db, user_ids)
        for user in users:
            html = template.format(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
            )
            self.send_email(
                subject=subject,
                html_content=html,
                sender_name=sender_name,
                sender_email=sender_email,
                recipients=[user.email],
            )
    
    def reset_password_email(self, email: str, token: str, name: str):
        link = f"{settings.BASE_URL}/password-reset?token={token}"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(base_dir, "templates", "password_reset_email.html")
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "templates",
            "password_reset.html",
        )
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        html_content = html_content.replace("{{name}}", name)
        html_content = html_content.replace("{link}", link)
        try:
            self.send_email(
            subject="Password Reset",
            html_content=html_content,
            sender_name="PACI SUPPORT",
            sender_email=settings.ADMIN_EMAIL,
            recipients=[email],
        )
            LOGGER.info(f"Password reset link sent to {email}.")
        except Exception as e:
            LOGGER.error(f"Error sending password reset email to {email}: {e}")
            raise ValueError("Error sending password reset email")
    
    def request_password_reset(self, db: Session, email: str):
        if not email:
            raise ValueError("Email is required.")
        user = self.user_service.get_user_by_email(db, email)
        if not user:
            raise ValueError("User not found")
        try:
            token = create_jwt(email)
            self.reset_password_email(email, token, user.first_name)
        except Exception as e:
            LOGGER.error("Error sending reset password email. %s", e)
            raise e

