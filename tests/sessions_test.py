import pytest
from datetime import datetime, timezone, timedelta
from repository.session_repository import SessionRepository
from services.session_service import SessionService

class TestSession:
    
    def test_complete_session_workflow(self, db_session, test_user):
        service = SessionService(db_session)
        token = "test_token_12345"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0"
        
        session = service.create_user_session(
            user_id=test_user.id,
            token=token,
            user_agent=user_agent,
            session_duration_hours=24
        )
        
        assert session is not None
        assert session.user_id == test_user.id
        assert session.token == token
        assert session.device_type == "desktop"
        
        found_session = service.get_session_by_token(token)
        assert found_session is not None
        assert found_session.id == session.id
        
        user_sessions = service.get_user_sessions(test_user.id)
        assert len(user_sessions) == 1
        assert user_sessions[0].token == token
        
        stats = service.get_session_stats(test_user.id)
        assert stats["active_sessions"] == 1
        assert stats["devices"]["desktop"] == 1
        
        invalidated = service.invalidate_session(token)
        assert invalidated is True
        
        found_after_logout = service.get_session_by_token(token)
        assert found_after_logout is None

    def test_device_detection(self, db_session, test_user):
        service = SessionService(db_session)
        
        test_cases = [
            ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0", "desktop"),
            ("Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)", "mobile"),
            ("Mozilla/5.0 (iPad; CPU OS 14_7_1 like Mac OS X)", "tablet"),
            ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", "desktop"),
            ("Mozilla/5.0 (Linux; Android 11; SM-G991B)", "mobile"),
            (None, "unknown")
        ]
        
        for i, (user_agent, expected_device) in enumerate(test_cases):
            session = service.create_user_session(
                user_id=test_user.id,
                token=f"device_test_token_{i}",
                user_agent=user_agent
            )
            
            assert session.device_type == expected_device

    def test_multiple_sessions_and_cleanup(self, db_session, test_user):
        service = SessionService(db_session)
        
        tokens = []
        for i in range(3):
            token = f"multi_session_token_{i}"
            session = service.create_user_session(
                user_id=test_user.id,
                token=token,
                user_agent=f"TestAgent{i}",
                session_duration_hours=24 if i < 2 else -1
            )
            tokens.append(token)
        
        all_sessions = service.get_user_sessions(test_user.id, active_only=False)
        active_sessions = service.get_user_sessions(test_user.id, active_only=True)
        
        assert len(all_sessions) == 3
        assert len(active_sessions) == 2
        
        cleaned_count = service.cleanup_expired_sessions()
        assert cleaned_count == 1
        
        remaining_count = service.invalidate_all_user_sessions(test_user.id)
        assert remaining_count == 2
        
        final_sessions = service.get_user_sessions(test_user.id)
        assert len(final_sessions) == 0

    def test_repository_direct_access(self, db_session, test_user):
        repo = SessionRepository(db_session)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        
        session = repo.create_session(
            user_id=test_user.id,
            token="repo_test_token",
            expires_at=expires_at,
            device_type="desktop"
        )
        
        assert session is not None
        
        found = repo.get_session_by_token("repo_test_token")
        assert found is not None
        assert found.id == session.id
        
        deleted = repo.delete_session_by_token("repo_test_token")
        assert deleted is True
        
        gone = repo.get_session_by_token("repo_test_token")
        assert gone is None

def test_session_imports():
    try:
        from models.session import Session
        from repository.session_repository import SessionRepository
        from services.session_service import SessionService
    except ImportError as e:
        raise AssertionError(f"Import error: {e}")