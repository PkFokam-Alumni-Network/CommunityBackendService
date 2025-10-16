from typing import Optional
from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError

from models.session import Session as SessionModel
from utils.retry import retry_on_db_error

SESSION_DURATION_HOURS = 24 * 7


class SessionRepository:
    @retry_on_db_error()
    def create_session(self, db: Session, user_id: int) -> SessionModel:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=SESSION_DURATION_HOURS)

        new_session = SessionModel(
            user_id=user_id,
            session_token=token,
            expires_at=expires_at,
        )

        try:
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            return new_session
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create session due to integrity constraint.")
        except OperationalError as e:
            db.rollback()
            raise ConnectionError(f"Database connection error: {e}")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An unexpected error occurred while creating session: {e}")

    @retry_on_db_error()
    def get_by_token(self, db: Session, token: str) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(
            SessionModel.session_token == token,
            SessionModel.expires_at > datetime.now(timezone.utc)
        ).first()

    @retry_on_db_error()
    def deactivate_session(self, db: Session, token: str) -> None:
        session = db.query(SessionModel).filter(SessionModel.session_token == token).first()
        if not session:
            raise ValueError("Session not found.")

        try:
            db.delete(session)
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Unable to deactivate session due to integrity constraint.")
        except OperationalError as e:
            db.rollback()
            raise ConnectionError(f"Database connection error: {e}")
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"An unexpected error occurred while deactivating session: {e}")

    @retry_on_db_error()
    def is_session_valid(self, db: Session, token: str) -> bool:
        """Helper method to check if a session is active and not expired."""
        session = self.get_by_token(db, token)
        return session is not None
