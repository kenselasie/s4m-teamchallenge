from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel


class User(BaseModel):

    __tablename__ = "users"

    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<User(username='{self.username}', is_active={self.is_active})>"
