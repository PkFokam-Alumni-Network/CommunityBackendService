# repository/session_repository.py - Database operations for sessions
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from models.session import Session
from utils.singleton_meta import SingletonMeta
from datetime import datetime

class SessionRepository(metaclass=SingletonMeta):
    """
    Repository for session database operations
    
    Handles:
    - Creating new sessions
    - Finding sessions by token or user
    - Deleting expired sessions
    - Managing user session limits
    """
    
    def __init__(self, db_session: DBSession):
        self.db: DBSession = db_session

    def create_session(self, user_id: int, token: str, expires_at: datetime, device_type: str = "unknown") -> Session:
        try:
            session = Session(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                device_type=device_type,
                created_at=datetime.utcnow()  
            )
            
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            
            return session
            
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Session already exists or invalid data: {e}")
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to create session: {e}")

    def get_session_by_token(self, token: str) -> Optional[Session]:
        return self.db.query(Session).filter(Session.token == token).first()

    def get_sessions_by_user(self, user_id: int) -> List[Session]:
        return self.db.query(Session).filter(Session.user_id == user_id).all()

    def get_active_sessions_by_user(self, user_id: int) -> List[Session]:
        now = datetime.utcnow()  
        return self.db.query(Session).filter(Session.user_id == user_id, Session.expires_at > now).all()

    def delete_session_by_token(self, token: str) -> bool:
        try:
            session = self.get_session_by_token(token)
            if session:
                self.db.delete(session)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete session: {e}")

    def delete_all_user_sessions(self, user_id: int) -> int:
        try:
            deleted_count = self.db.query(Session).filter(Session.user_id == user_id).delete()
            
            self.db.commit()
            return deleted_count
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to delete user sessions: {e}")

    def cleanup_expired_sessions(self) -> int:
        try:
            now = datetime.utcnow()  
            deleted_count = self.db.query(Session).filter(Session.expires_at <= now).delete()
            
            self.db.commit()
            return deleted_count
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to cleanup expired sessions: {e}")