"""
PDF model for storing PDF metadata and information.
"""

from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class PDF(BaseModel):
    """PDF model for storing PDF metadata."""
    
    __tablename__ = "pdfs"
    
    title = Column(String(255), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_type = Column(String(100), default="application/pdf")
    file_size = Column(Integer, nullable=False)  # Size in bytes
    total_pages = Column(Integer, nullable=False)
    
    # Metadata
    author = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    keywords = Column(Text, nullable=True)
    
    # File processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)
    
    # Remove user relationship for simplified PDF-only functionality
    
    # Chunks relationship
    chunks = relationship("PDFChunk", back_populates="pdf", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PDF(title='{self.title}', pages={self.total_pages}, status='{self.processing_status}')>"
    
    @property
    def file_size_mb(self) -> float:
        """Return file size in MB."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_processed(self) -> bool:
        """Check if PDF has been successfully processed."""
        return self.processing_status == "completed"