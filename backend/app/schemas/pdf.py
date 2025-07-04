"""
PDF schemas for request/response validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, TimestampMixin
from app.schemas.pdf_chunk import PDFChunkResponse


class PDFBase(BaseModel):
    """Base PDF schema."""
    
    title: str = Field(..., min_length=1, max_length=255, description="PDF title")


class PDFCreate(PDFBase):
    """Schema for creating a new PDF."""
    
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    total_pages: int = Field(..., gt=0, description="Total number of pages")
    
    # Optional metadata
    author: Optional[str] = Field(None, max_length=255, description="PDF author")
    subject: Optional[str] = Field(None, max_length=500, description="PDF subject")
    keywords: Optional[str] = Field(None, description="PDF keywords")


class PDFUpdate(BaseModel):
    """Schema for updating PDF metadata."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = Field(None, max_length=500)
    keywords: Optional[str] = Field(None)


class PDFResponse(BaseSchema, TimestampMixin):
    """Schema for PDF response."""
    
    id: int
    title: str
    filename: str
    content_type: str
    file_size: int
    total_pages: int
    processing_status: str
    processing_error: Optional[str] = None
    
    # Metadata
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    
    # Computed properties
    file_size_mb: float
    is_processed: bool
    
    # Remove owner info for simplified PDF-only functionality


class PDFListResponse(BaseModel):
    """Schema for paginated PDF list response."""
    
    items: List[PDFResponse]
    total: int
    page: int
    size: int
    pages: int


class PDFDetailResponse(PDFResponse):
    """Schema for detailed PDF response with chunks."""
    
    chunks: List[PDFChunkResponse] = []