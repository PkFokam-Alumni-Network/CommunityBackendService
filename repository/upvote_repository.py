from typing import Optional, List
from sqlalchemy.orm import Session
from models.upvote import Upvote
from schemas.upvote import UpvoteCreate

class upvoteRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def toggle_upvote_on_post(self, upvote: Upvote) -> bool:
        """
        Toggles an upvote. Returns True if upvote was added, False if removed.
        """
        existing_upvote = self.db.query(Upvote).filter(
            Upvote.user_id == upvote.user_id,
            Upvote.post_id == upvote.post_id
        ).first()

        try: 
            if existing_upvote:
                self.db.delete(existing_upvote)
                self.db.commit()
                return False # Upvote removed
            else:
                self.db.add(upvote)
                self.db.commit()
                self.db.refresh(upvote)
                return True # Upvote added
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Error toggling upvote: {e}")

    def count_upvotes(self, post_id: int) -> int:
        return self.db.query(Upvote).filter(Upvote.post_id == post_id).count()
