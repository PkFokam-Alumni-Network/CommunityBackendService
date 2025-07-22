from typing import List
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sqlalchemy.orm import Session
from models.user import User
from models.announcement import Announcement
from logging_config import LOGGER
from settings import settings  
from pathlib import Path
from repository.user_repository import UserRepository
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os


class EmailService:
    def __init__(self):
        self.sender_name = settings.ADMIN_NAME
        self.sender_email = settings.ADMIN_EMAIL
        self.api_key = settings.BREVO_API_KEY  

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        self.api_client = sib_api_v3_sdk.ApiClient(configuration)
        self.email_api = sib_api_v3_sdk.TransactionalEmailsApi(self.api_client)

        self.user_repo = UserRepository()
        
        base_dir = Path(__file__).resolve().parent
        templates_path = base_dir / "templates"
        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=templates_path),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _send_email(self, to_email: str, subject: str, html_content: str) -> None:
        send_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": to_email}],
            sender={"name": self.sender_name, "email": self.sender_email},
            subject=subject,
            html_content=html_content
        )
        self.email_api.send_transac_email(send_email)

    def send_general_email(self, db: Session, announcement: Announcement) -> None:
        try:
            users = self.user_repo.get_users(db, active=False)
            if not users:
                LOGGER.warning("No users found.")
                return

            subject = f"📢 New Announcement: {announcement.title}"
            template = self.template_env.get_template("announcement_email.html")

            for user in users:
                if not user.email:
                    continue

                html_body = template.render(
                    title=announcement.title,
                    description=announcement.description,
                    date=announcement.announcement_date.strftime('%Y-%m-%d %H:%M'),
                    first_name=user.first_name or "User",
                    last_name=user.last_name or ""
                )

                self._send_email(user.email, subject, html_body)

            LOGGER.info(f"Announcement email sent to {len(users)} users.")

        except ApiException as e:
            LOGGER.error(f"Brevo API failed: {e}")
            raise

        except Exception as e:
            LOGGER.error(f"Unexpected error in sending email: {e}")
            raise

    def send_specific_email(self, user: User, announcement: Announcement) -> None:
        try:
            if not user.email:
                LOGGER.warning(f"User {user.id} has no email.")
                return

            subject = f"📢 New Announcement: {announcement.title}"
            template = self.template_env.get_template("announcement_email.html")

            html_body = template.render(
                title=announcement.title,
                description=announcement.description,
                date=announcement.announcement_date.strftime('%Y-%m-%d %H:%M'),
                first_name=user.first_name or "User",
                last_name=user.last_name or ""
            )

            self._send_email(user.email, subject, html_body)
            LOGGER.info(f"Announcement email sent to user {user.id}")

        except ApiException as e:
            LOGGER.error(f"Brevo API failed for user {user.id}: {e}")
            raise

        except Exception as e:
            LOGGER.error(f"Error sending email to user {user.id}: {e}")
            raise
