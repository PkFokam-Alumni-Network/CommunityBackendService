from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from models.announcement import Announcement
from services.email_service import EmailService
import pytest


@pytest.fixture
def mock_announcement():
    return Announcement(
        id=1,
        title="Test Announcement",
        description="This is a test email announcement.",
        announcement_date="2023-10-10T10:00:00",
        announcement_deadline="2023-12-31T23:59:59",
        image="test_image_url"
    )


def test_send_announcement_email_success(mock_announcement):
    mock_db = MagicMock(spec=Session)
    mock_users = [MagicMock(email="user1@example.com"), MagicMock(email="user2@example.com")]
    mock_db.query().all.return_value = mock_users

    email_service = EmailService()

    with patch.object(email_service.email_api, 'send_transac_email', return_value=True) as mock_send:
        email_service.send_announcement_email(mock_db, mock_announcement)
        assert mock_send.called
        assert mock_send.call_count == 1


def test_send_announcement_email_no_users(mock_announcement):
    mock_db = MagicMock(spec=Session)
    mock_db.query().all.return_value = []

    email_service = EmailService()

    with patch.object(email_service.email_api, 'send_transac_email') as mock_send:
        email_service.send_announcement_email(mock_db, mock_announcement)
        mock_send.assert_not_called()


def test_send_announcement_email_api_exception(mock_announcement):
    mock_db = MagicMock(spec=Session)
    mock_db.query().all.return_value = [MagicMock(email="user@example.com")]

    email_service = EmailService()

    with patch.object(email_service.email_api, 'send_transac_email', side_effect=Exception("API Error")):
        with pytest.raises(Exception) as exc_info:
            email_service.send_announcement_email(mock_db, mock_announcement)
        assert "API Error" in str(exc_info.value)
