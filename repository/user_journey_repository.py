from sqlalchemy.orm import Session
from models.user_journey import UserJourney
from typing import Optional, List
from datetime import datetime
from utils.retry import retry_on_db_error

class UserJourneyRepository:

    @retry_on_db_error()
    def create_log(
        self,
        db: Session,
        user_id: int,
        action: str,
        session_token: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        extra_metadata: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserJourney:
        journey_log = UserJourney(
            user_id=user_id,
            session_token=session_token,
            action=action,
            endpoint=endpoint,
            method=method,
            extra_metadata=extra_metadata,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(journey_log)
        db.commit()
        db.refresh(journey_log)
        return journey_log

    @retry_on_db_error()
    def get_user_journey(
        self,
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserJourney]:
        return (
            db.query(UserJourney)
            .filter(UserJourney.user_id == user_id)
            .order_by(UserJourney.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @retry_on_db_error()
    def get_session_journey(
        self,
        db: Session,
        session_token: str
    ) -> List[UserJourney]:
        return (
            db.query(UserJourney)
            .filter(UserJourney.session_token == session_token)
            .order_by(UserJourney.timestamp.asc())
            .all()
        )

    @retry_on_db_error()
    def get_action_count(
        self,
        db: Session,
        user_id: int,
        action: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        query = db.query(UserJourney).filter(
            UserJourney.user_id == user_id,
            UserJourney.action == action
        )
        
        if start_date:
            query = query.filter(UserJourney.timestamp >= start_date)
        if end_date:
            query = query.filter(UserJourney.timestamp <= end_date)
        
        return query.count()