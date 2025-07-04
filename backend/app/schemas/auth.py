

from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """JWT token response schema."""
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema for JWT payload."""
    
    sub: Optional[str] = None
    exp: Optional[int] = None


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema for user response."""
    
    id: int
    username: str
    is_active: bool