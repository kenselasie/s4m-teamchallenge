"""
PDF Chunk repository for chunk-specific database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models.pdf_chunk import PDFChunk
from app.repositories.base import BaseRepository


class PDFChunkRepository(BaseRepository[PDFChunk]):
    """Repository for PDFChunk model operations."""
    
    def __init__(self, db: Session):
        super().__init__(PDFChunk, db)
    
    def get_by_pdf(self, pdf_id: int, skip: int = 0, limit: int = 100) -> List[PDFChunk]:
        """Get chunks for a specific PDF."""
        return self.db.query(PDFChunk).filter(
            PDFChunk.pdf_id == pdf_id
        ).order_by(PDFChunk.chunk_number).offset(skip).limit(limit).all()
    
    def get_by_page(self, pdf_id: int, page_number: int) -> List[PDFChunk]:
        """Get chunks for a specific page."""
        return self.db.query(PDFChunk).filter(
            PDFChunk.pdf_id == pdf_id,
            PDFChunk.page_number == page_number
        ).order_by(PDFChunk.chunk_number).all()
    
    def search_content(self, pdf_id: int, search_term: str, skip: int = 0, limit: int = 100) -> List[PDFChunk]:
        """Search chunks by content."""
        return self.db.query(PDFChunk).filter(
            PDFChunk.pdf_id == pdf_id,
            PDFChunk.content.ilike(f"%{search_term}%")
        ).order_by(PDFChunk.chunk_number).offset(skip).limit(limit).all()
    
    def search_all_content(self, search_term: str, skip: int = 0, limit: int = 100) -> List[PDFChunk]:
        """Search chunks across all PDFs."""
        return self.db.query(PDFChunk).filter(
            PDFChunk.content.ilike(f"%{search_term}%")
        ).order_by(desc(PDFChunk.created_at)).offset(skip).limit(limit).all()
    
    def count_search_content(self, search_term: str, pdf_id: Optional[int] = None) -> int:
        """Count search results."""
        query = self.db.query(PDFChunk).filter(
            PDFChunk.content.ilike(f"%{search_term}%")
        )
        
        if pdf_id:
            query = query.filter(PDFChunk.pdf_id == pdf_id)
        
        return query.count()
    
    def count_search_all_content(self, search_term: str) -> int:
        """Count search results across all PDFs."""
        return self.db.query(PDFChunk).filter(
            PDFChunk.content.ilike(f"%{search_term}%")
        ).count()
    
    def count_by_pdf(self, pdf_id: int) -> int:
        """Count chunks for a PDF."""
        return self.db.query(PDFChunk).filter(PDFChunk.pdf_id == pdf_id).count()
    
    def get_chunk_by_number(self, pdf_id: int, chunk_number: int) -> Optional[PDFChunk]:
        """Get specific chunk by number."""
        return self.db.query(PDFChunk).filter(
            PDFChunk.pdf_id == pdf_id,
            PDFChunk.chunk_number == chunk_number
        ).first()
    
    def delete_by_pdf(self, pdf_id: int) -> int:
        """Delete all chunks for a PDF."""
        count = self.db.query(PDFChunk).filter(PDFChunk.pdf_id == pdf_id).count()
        self.db.query(PDFChunk).filter(PDFChunk.pdf_id == pdf_id).delete()
        self.db.commit()
        return count
    
    def get_content_stats(self, pdf_id: int) -> dict:
        """Get content statistics for a PDF."""
        from sqlalchemy import func
        
        result = self.db.query(
            func.count(PDFChunk.id).label('total_chunks'),
            func.sum(PDFChunk.word_count).label('total_words'),
            func.sum(PDFChunk.character_count).label('total_characters'),
            func.avg(PDFChunk.word_count).label('avg_words_per_chunk'),
            func.max(PDFChunk.page_number).label('max_page')
        ).filter(PDFChunk.pdf_id == pdf_id).first()
        
        return {
            'total_chunks': result.total_chunks or 0,
            'total_words': result.total_words or 0,
            'total_characters': result.total_characters or 0,
            'avg_words_per_chunk': float(result.avg_words_per_chunk or 0),
            'max_page': result.max_page or 0
        }
    
    def bulk_create(self, chunks_data: List[dict]) -> List[PDFChunk]:
        """Create multiple chunks in bulk."""
        chunks = []
        for chunk_data in chunks_data:
            chunk = PDFChunk(**chunk_data)
            chunk.update_stats()  # Update word and character counts
            chunks.append(chunk)
        
        self.db.add_all(chunks)
        self.db.commit()
        
        for chunk in chunks:
            self.db.refresh(chunk)
        
        return chunks