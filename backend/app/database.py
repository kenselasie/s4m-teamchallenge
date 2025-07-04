"""
Database configuration and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.base import Base

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./app.db"
)

engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Only needed for SQLite
        echo=False  # Set to True for SQL logging in development
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency to get database session.
    Ensures proper session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all tables - use with caution!"""
    Base.metadata.drop_all(bind=engine)


def seed_demo_user():
    """Seed the demo user into the database."""
    from .services.auth_service import AuthService
    
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        demo_user = auth_service.create_demo_user()
        print(f"Demo user created/verified: {demo_user.username}")
    except Exception as e:
        print(f"Error creating demo user: {e}")
    finally:
        db.close()