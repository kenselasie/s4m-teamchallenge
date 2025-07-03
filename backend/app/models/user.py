"""
User model for authentication.
"""

from sqlalchemy import Column, String, Boolean
from .base import BaseModel


class User(BaseModel):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<User(username='{self.username}', is_active={self.is_active})>"