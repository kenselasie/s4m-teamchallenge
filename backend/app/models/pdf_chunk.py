"""
PDF Chunk model for storing parsed PDF content sections.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class PDFChunk(BaseModel):
    """PDF Chunk model for storing parsed content sections."""
    
    __tablename__ = "pdf_chunks"
    
    pdf_id = Column(Integer, ForeignKey("pdfs.id"), nullable=False, index=True)
    chunk_number = Column(Integer, nullable=False)  # Sequential chunk number
    page_number = Column(Integer, nullable=False, index=True)  # Original page number
    
    # Content
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, image, table, etc.
    
    # Metadata
    word_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    
    # Additional metadata stored as JSON
    chunk_metadata = Column(JSON, nullable=True)
    
    # Relationships
    pdf = relationship("PDF", back_populates="chunks")
    
    def __repr__(self):
        return f"<PDFChunk(pdf_id={self.pdf_id}, chunk={self.chunk_number}, page={self.page_number})>"
    
    @property
    def preview(self) -> str:
        """Return a preview of the content (first 100 characters)."""
        if len(self.content) <= 100:
            return self.content
        return self.content[:100] + "..."
