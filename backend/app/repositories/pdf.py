from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.models.pdf import PDF
from app.repositories.base import BaseRepository


class PDFRepository(BaseRepository[PDF]):
    def __init__(self, db: Session):
        super().__init__(PDF, db)

    def get_with_chunks(self, pdf_id: int) -> Optional[PDF]:
        return (
            self.db.query(PDF)
            .options(joinedload(PDF.chunks))
            .filter(PDF.id == pdf_id)
            .first()
        )

    def update_processing_status(
        self, pdf_id: int, status: str, error: Optional[str] = None
    ) -> Optional[PDF]:
        pdf = self.get(pdf_id)
        if pdf:
            pdf.processing_status = status
            if error:
                pdf.processing_error = error
            self.db.commit()
            self.db.refresh(pdf)
        return pdf
