"""
FastAPI application for PDF parsing and chunking.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import create_tables, seed_demo_user
from .controllers.pdf_controller import router as pdf_router
from .controllers.user_controller import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Create database tables on startup
    create_tables()
    # Seed demo user
    seed_demo_user()
    yield
    # Cleanup on shutdown if needed

app = FastAPI(
    title="Code Challenge API",
    description="API for uploading, parsing, and searching PDF documents",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(pdf_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "PDF Parser API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 