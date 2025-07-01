from typing import Optional, List
from sqlalchemy.orm import Session
from models.upvote import Upvote
from utils.singleton_meta import SingletonMeta

class UpvoteRepository(metaclass=SingletonMeta):
    def __init__(self, session: Session):
        self.db: Session = session

    def get_upvote_by_user_and_post(self, user_id: int, post_id: int) -> Optional[Upvote]:
        return self.db.query(Upvote).filter(Upvote.user_id == user_id, Upvote.post_id == post_id).first()

    def create_upvote(self, upvote: Upvote) -> Upvote:
        self.db.add(upvote)
        self.db.commit()
        self.db.refresh(upvote)
        return upvote

    def delete_upvote(self, upvote: Upvote) -> None:
        self.db.delete(upvote)
        self.db.commit()

    def count_upvotes(self, post_id: int) -> int:
        return self.db.query(Upvote).filter(Upvote.post_id == post_id).count()