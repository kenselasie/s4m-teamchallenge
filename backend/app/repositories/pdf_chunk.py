from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from app.models.pdf_chunk import PDFChunk
from app.repositories.base import BaseRepository


class PDFChunkRepository(BaseRepository[PDFChunk]):
    def __init__(self, db: Session):
        super().__init__(PDFChunk, db)

    def get_by_pdf(
        self, pdf_id: int, skip: int = 0, limit: int = 100
    ) -> List[PDFChunk]:
        return (
            self.db.query(PDFChunk)
            .filter(PDFChunk.pdf_id == pdf_id)
            .order_by(PDFChunk.chunk_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_content(
        self, pdf_id: int, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[PDFChunk]:
        return (
            self.db.query(PDFChunk)
            .filter(
                PDFChunk.pdf_id == pdf_id, PDFChunk.content.ilike(f"%{search_term}%")
            )
            .order_by(PDFChunk.chunk_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_all_content(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[PDFChunk]:
        return (
            self.db.query(PDFChunk)
            .filter(PDFChunk.content.ilike(f"%{search_term}%"))
            .order_by(desc(PDFChunk.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_search_content(
        self, search_term: str, pdf_id: Optional[int] = None
    ) -> int:
        query = self.db.query(PDFChunk).filter(
            PDFChunk.content.ilike(f"%{search_term}%")
        )

        if pdf_id:
            query = query.filter(PDFChunk.pdf_id == pdf_id)

        return query.count()

    def count_search_all_content(self, search_term: str) -> int:
        """Count search results across all PDFs."""
        return (
            self.db.query(PDFChunk)
            .filter(PDFChunk.content.ilike(f"%{search_term}%"))
            .count()
        )

    def count_by_pdf(self, pdf_id: int) -> int:
        """Count chunks for a specific PDF."""
        return self.db.query(PDFChunk).filter(PDFChunk.pdf_id == pdf_id).count()

    def bulk_create(self, chunks_data: List[dict]) -> List[PDFChunk]:
        """Create multiple chunks in bulk."""
        chunks = []
        for chunk_data in chunks_data:
            chunk = PDFChunk(**chunk_data)
            chunks.append(chunk)

        self.db.add_all(chunks)
        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks
