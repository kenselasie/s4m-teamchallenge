"""
Base model class with common fields and functionality.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """Abstract base model with common fields."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }