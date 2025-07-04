"""
Authentication service for user authentication and authorization.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user import UserRepository

# Security configuration
SECRET_KEY = "your-secret-key-for-development"  # Should be from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = self.user_repo.get_active_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return username."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        username = self.verify_token(token)
        if username is None:
            return None
        
        user = self.user_repo.get_active_user_by_username(username)
        return user
    
    def create_demo_user(self) -> User:
        """Create the demo user if it doesn't exist."""
        demo_username = "demo@example.com"
        demo_password = "demo123"
        
        # Check if demo user already exists
        existing_user = self.user_repo.get_by_username(demo_username)
        if existing_user:
            return existing_user
        
        # Create demo user
        hashed_password = self.get_password_hash(demo_password)
        user_data = {
            "username": demo_username,
            "hashed_password": hashed_password,
            "is_active": True
        }
        
        return self.user_repo.create(user_data)