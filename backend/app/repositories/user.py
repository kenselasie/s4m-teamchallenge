from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_active_user_by_username(self, username: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.username == username, User.is_active == True)
            .first()
        )

    def username_exists(self, username: str) -> bool:
        return self.db.query(User).filter(User.username == username).first() is not None
