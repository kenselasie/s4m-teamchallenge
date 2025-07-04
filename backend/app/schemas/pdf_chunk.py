"""
PDF Chunk schemas for request/response validation.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, TimestampMixin


class PDFChunkBase(BaseModel):
    """Base PDF chunk schema."""
    
    chunk_number: int = Field(..., ge=1, description="Sequential chunk number")
    page_number: int = Field(..., ge=1, description="Original page number")
    content: str = Field(..., min_length=1, description="Chunk content")
    content_type: str = Field(default="text", description="Content type")


class PDFChunkCreate(PDFChunkBase):
    """Schema for creating a new PDF chunk."""
    
    pdf_id: int = Field(..., description="PDF ID this chunk belongs to")
    chunk_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PDFChunkResponse(BaseSchema, TimestampMixin):
    """Schema for PDF chunk response."""
    
    id: int
    pdf_id: int
    chunk_number: int
    page_number: int
    content: str
    content_type: str
    word_count: int
    character_count: int
    chunk_metadata: Optional[Dict[str, Any]] = None
    
    # Computed properties
    preview: str


class PDFChunkListResponse(BaseModel):
    """Schema for paginated PDF chunk list response."""
    
    items: List[PDFChunkResponse]
    total: int
    page: int
    size: int
    pages: int
    pdf_id: int


class PDFChunkSearchResponse(BaseModel):
    """Schema for paginated search results response."""
    
    items: List[PDFChunkResponse]
    total: int
    page: int
    size: int
    pages: int
    query: str
    pdf_id: Optional[int] = None