"""
User controller for authentication endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.auth import Token, UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter(tags=["authentication"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    auth_service = AuthService(db)
    
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected", response_model=UserResponse)
async def protected_route(current_user = Depends(get_current_user)):
    """Protected route that requires authentication."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active
    ) 