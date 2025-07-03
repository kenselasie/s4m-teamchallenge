"""
Base schema classes with common configurations.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    
    created_at: datetime
    updated_at: datetime