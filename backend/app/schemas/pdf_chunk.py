from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, TimestampMixin


class PDFChunkBase(BaseModel):
    chunk_number: int = Field(..., ge=1, description="Sequential chunk number")
    page_number: int = Field(..., ge=1, description="Original page number")
    content: str = Field(..., min_length=1, description="Chunk content")
    content_type: str = Field(default="text", description="Content type")


class PDFChunkCreate(PDFChunkBase):
    pdf_id: int = Field(..., description="PDF ID this chunk belongs to")
    chunk_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )


class PDFChunkResponse(BaseSchema, TimestampMixin):

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
    items: List[PDFChunkResponse]
    total: int
    page: int
    size: int
    pages: int
    pdf_id: int


class PDFChunkSearchResponse(BaseModel):
    items: List[PDFChunkResponse]
    total: int
    page: int
    size: int
    pages: int
    query: str
    pdf_id: Optional[int] = None
