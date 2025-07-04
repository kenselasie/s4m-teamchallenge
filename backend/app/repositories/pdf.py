from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.models.pdf import PDF
from app.repositories.base import BaseRepository


class PDFRepository(BaseRepository[PDF]):
    """Repository for PDF model operations."""
    
    def __init__(self, db: Session):
        super().__init__(PDF, db)
    
    def get_with_chunks(self, pdf_id: int) -> Optional[PDF]:
        """Get PDF with all its chunks."""
        return self.db.query(PDF).options(joinedload(PDF.chunks)).filter(PDF.id == pdf_id).first()
    
    def get_by_filename(self, filename: str) -> Optional[PDF]:
        """Get PDF by filename."""
        return self.db.query(PDF).filter(PDF.filename == filename).first()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[PDF]:
        """Get PDFs by processing status."""
        return self.db.query(PDF).filter(
            PDF.processing_status == status
        ).order_by(desc(PDF.created_at)).offset(skip).limit(limit).all()
    
    def get_processed_pdfs(self, skip: int = 0, limit: int = 100) -> List[PDF]:
        """Get successfully processed PDFs."""
        return self.db.query(PDF).filter(
            PDF.processing_status == "completed"
        ).order_by(desc(PDF.created_at)).offset(skip).limit(limit).all()
    
    def search_pdfs(self, search_term: str, skip: int = 0, limit: int = 100) -> List[PDF]:
        """Search PDFs by title, filename, author, or subject."""
        return self.db.query(PDF).filter(
            or_(
                PDF.title.ilike(f"%{search_term}%"),
                PDF.filename.ilike(f"%{search_term}%"),
                PDF.author.ilike(f"%{search_term}%"),
                PDF.subject.ilike(f"%{search_term}%"),
                PDF.keywords.ilike(f"%{search_term}%")
            )
        ).order_by(desc(PDF.created_at)).offset(skip).limit(limit).all()
    
    def count_by_status(self, status: str) -> int:
        """Count PDFs by status."""
        return self.db.query(PDF).filter(
            PDF.processing_status == status
        ).count()
    
    def update_processing_status(self, pdf_id: int, status: str, error: Optional[str] = None) -> Optional[PDF]:
        """Update PDF processing status."""
        pdf = self.get(pdf_id)
        if pdf:
            pdf.processing_status = status
            if error:
                pdf.processing_error = error
            self.db.commit()
            self.db.refresh(pdf)
        return pdf
    
