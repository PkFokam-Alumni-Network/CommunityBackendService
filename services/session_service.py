from datetime import datetime, timedelta,timezone
from typing import Optional
from models.session import Session
from sqlalchemy.orm import Session as DBSession
from utils.singleton_meta import SingletonMeta
from repository.session_repository import SessionRepository
from utils.func_utils import detect_device_type


class SessionService(metaclass=SingletonMeta):
    def __init__(self, db_session: DBSession):   
        self.repository = SessionRepository(db_session)
        
    def create_user_session(self, user_id: int, token: str, user_agent: str, session_duration_hours: int = 24) -> Session:
        self.delete_all_user_sessions(user_id)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=session_duration_hours)
        expires_at = expires_at.replace(tzinfo=None)
        device_type = detect_device_type(user_agent)
        session = self.repository.create_session(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_type=device_type
        )
        return session
    
    def get_session_by_token(self, token: str) -> Optional[Session]:
        session = self.repository.get_session_by_token(token)
        if session and session.expires_at > datetime.utcnow():  
            return session
        if session:
            self.repository.delete_session_by_token(token)
        return None
    
    def get_user_sessions(self, user_id: int, active_only: bool = True) -> list[Session]:
        if active_only:
            return self.repository.get_active_sessions_by_user(user_id)
        return self.repository.get_sessions_by_user(user_id)
    
    def invalidate_session(self, token: str) -> bool:
        return self.repository.delete_session_by_token(token)
    
    def delete_all_user_sessions(self, user_id: int) -> int:
        return self.repository.delete_all_user_sessions(user_id)
        
    def cleanup_expired_sessions(self) -> int:
        return self.repository.cleanup_expired_sessions()
        