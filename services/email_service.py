from typing import List
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from sqlalchemy.orm import Session
from models.user import User
from models.announcement import Announcement
from logging_config import LOGGER
from settings import settings  


class EmailService:
    def __init__(self):
        self.sender_name = settings.ADMIN_NAME
        self.sender_email = settings.ADMIN_EMAIL
        self.api_key = settings.BREVO_API_KEY  

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key
        self.api_client = sib_api_v3_sdk.ApiClient(configuration)
        self.email_api = sib_api_v3_sdk.TransactionalEmailsApi(self.api_client)

    def get_all_user_emails(self, db: Session) -> List[str]:
        users = db.query(User).all()
        return [user.email for user in users if user.email]

    def send_announcement_email(self, db: Session, announcement: Announcement) -> None:
        try:
            recipient_emails = self.get_all_user_emails(db)
            if not recipient_emails:
                LOGGER.warning("No recipient emails found.")
                return

            subject = f"📢 New Announcement: {announcement.title}"
            body = f"""
            <h3>{announcement.title}</h3>
            <p>{announcement.description}</p>
            <p><strong>Date:</strong> {announcement.announcement_date.strftime('%Y-%m-%d %H:%M')}</p>
            """

            to_list = [{"email": email} for email in recipient_emails]

            send_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to_list,
                sender={"name": self.sender_name, "email": self.sender_email},
                subject=subject,
                html_content=body
            )

            self.email_api.send_transac_email(send_email)
            LOGGER.info(f"Announcement email sent to {len(recipient_emails)} users.")

        except ApiException as e:
            LOGGER.error(f"Brevo API failed: {e}")
            raise

        except Exception as e:
            LOGGER.error(f"Unexpected error in sending email: {e}")
            raise
