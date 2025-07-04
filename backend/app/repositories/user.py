"""
User repository for user-specific database operations.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_active_user_by_username(self, username: str) -> Optional[User]:
        """Get active user by username."""
        return self.db.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists."""
        return self.db.query(User).filter(User.username == username).first() is not None