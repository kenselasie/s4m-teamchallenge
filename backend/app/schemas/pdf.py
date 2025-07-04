from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.base import BaseSchema, TimestampMixin
from app.schemas.pdf_chunk import PDFChunkResponse


class PDFBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="PDF title")


class PDFCreate(PDFBase):

    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., gt=0, description="File size in bytes")
    total_pages: int = Field(..., gt=0, description="Total number of pages")
    author: Optional[str] = Field(None, max_length=255, description="PDF author")
    subject: Optional[str] = Field(None, max_length=500, description="PDF subject")
    keywords: Optional[str] = Field(None, description="PDF keywords")


class PDFUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    subject: Optional[str] = Field(None, max_length=500)
    keywords: Optional[str] = Field(None)


class PDFResponse(BaseSchema, TimestampMixin):
    id: int
    title: str
    filename: str
    content_type: str
    file_size: int
    total_pages: int
    processing_status: str
    processing_error: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None

    # Computed properties
    file_size_mb: float
    is_processed: bool


class PDFListResponse(BaseModel):
    items: List[PDFResponse]
    total: int
    page: int
    size: int
    pages: int


class PDFDetailResponse(PDFResponse):
    chunks: List[PDFChunkResponse] = []
