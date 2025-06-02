from datetime import datetime, timedelta
from typing import Optional
from models.session import Session
from sqlalchemy.orm import Session as DBSession
from utils.singleton_meta import SingletonMeta
from repository.session_repository import SessionRepository

class SessionService(metaclass=SingletonMeta):
    def __init__(self, db_session: DBSession):   
        self.repository = SessionRepository(db_session)
        
    def create_user_session(self, user_id: int, token: str, user_agent: str, session_duration_hours: int = 24) -> Session:
        expires_at = datetime.utcnow() + timedelta(hours=session_duration_hours) 
        device_type = self._detect_device_type(user_agent)
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
    
    def invalidate_all_user_sessions(self, user_id: int) -> int:
        return self.repository.delete_all_user_sessions(user_id)
        
    def cleanup_expired_sessions(self) -> int:
        return self.repository.cleanup_expired_sessions()
        
    def _detect_device_type(self, user_agent: str) -> str:
        if not user_agent:
            return "unknown"
        user_agent_lower = user_agent.lower()
        mobile_indicators = ["mobile", "android", "iphone", "samsung", "huawei", "xiaomi"]
        tablet_indicators = ["ipad", "tablet"]
        desktop_indicators = ["windows", "macintosh", "linux", "ubuntu"]
        
        for indicator in mobile_indicators:
            if indicator in user_agent_lower:
                return "mobile"
        for indicator in tablet_indicators:
            if indicator in user_agent_lower:
                return "tablet"
        for indicator in desktop_indicators:
            if indicator in user_agent_lower:
                return "desktop"
        return "unknown"
        
    def get_session_stats(self, user_id: int) -> dict:
        active_sessions = self.get_user_sessions(user_id, active_only=True)
        all_sessions = self.get_user_sessions(user_id, active_only=False)
        device_counts = {}
        for session in active_sessions:
            device_type = session.device_type
            device_counts[device_type] = device_counts.get(device_type, 0) + 1
        return {
            "active_sessions": len(active_sessions),
            "total_sessions": len(all_sessions),
            "devices": device_counts,
            "oldest_session": min((s.created_at for s in active_sessions)) 
            if active_sessions else None,
            "newest_session": max((s.created_at for s in active_sessions))
            if active_sessions else None,
        }