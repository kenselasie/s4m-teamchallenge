"""
PDF service for parsing and chunking operations.
"""

import os
import tempfile
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
import pdfplumber
from sqlalchemy.orm import Session
from app.models.pdf import PDF
from app.models.pdf_chunk import PDFChunk
from app.repositories.pdf import PDFRepository
from app.repositories.pdf_chunk import PDFChunkRepository


class PDFService:
    """Service for PDF operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.pdf_repo = PDFRepository(db)
        self.chunk_repo = PDFChunkRepository(db)
    
    async def upload_and_parse_pdf(self, file: UploadFile, title: Optional[str] = None) -> PDF:
        """Upload and parse a PDF file."""
        # Validate file type
        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are allowed")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Extract metadata and create PDF record
            metadata = self._extract_pdf_metadata(temp_file_path)
            
            pdf_data = {
                "title": title or file.filename or "Untitled PDF",
                "filename": file.filename,
                "file_path": temp_file_path,
                "content_type": file.content_type,
                "file_size": len(content),
                "total_pages": metadata["total_pages"],
                "author": metadata.get("author"),
                "subject": metadata.get("subject"),
                "keywords": metadata.get("keywords"),
                "processing_status": "processing"
            }
            
            # Create PDF record
            pdf = self.pdf_repo.create(pdf_data)
            
            # Parse and chunk the PDF
            chunks = self._parse_pdf_to_chunks(temp_file_path, pdf.id)
            
            # Create chunks in database
            if chunks:
                self.chunk_repo.bulk_create(chunks)
                self.pdf_repo.update_processing_status(pdf.id, "completed")
            else:
                self.pdf_repo.update_processing_status(pdf.id, "failed", "No content extracted")
            
            return pdf
            
        except Exception as e:
            # Update status to failed
            if 'pdf' in locals():
                self.pdf_repo.update_processing_status(pdf.id, "failed", str(e))
            raise
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def _extract_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF file."""
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = pdf.metadata or {}
                return {
                    "total_pages": len(pdf.pages),
                    "author": metadata.get("Author"),
                    "subject": metadata.get("Subject"),
                    "keywords": metadata.get("Keywords"),
                    "title": metadata.get("Title"),
                    "creator": metadata.get("Creator"),
                    "producer": metadata.get("Producer")
                }
        except Exception as e:
            raise ValueError(f"Failed to extract PDF metadata: {str(e)}")
    
    def _parse_pdf_to_chunks(self, file_path: str, pdf_id: int) -> List[Dict[str, Any]]:
        """Parse PDF and split into chunks by pages."""
        chunks = []
        chunk_counter = 1
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text from page
                    text = page.extract_text()
                    
                    if text and text.strip():
                        # Split page into smaller chunks if it's too long
                        page_chunks = self._split_text_into_chunks(text, page_num)
                        
                        # Create chunk data for each chunk
                        for chunk_idx, chunk_text in enumerate(page_chunks):
                            chunk_data = {
                                "pdf_id": pdf_id,
                                "chunk_number": chunk_counter,
                                "page_number": page_num,
                                "content": chunk_text,
                                "content_type": "text",
                                "word_count": len(chunk_text.split()),
                                "character_count": len(chunk_text),
                                "chunk_metadata": {
                                    "page_width": page.width,
                                    "page_height": page.height,
                                    "chunk_index_in_page": chunk_idx
                                }
                            }
                            
                            chunks.append(chunk_data)
                            chunk_counter += 1
                        
        except Exception as e:
            raise ValueError(f"Failed to parse PDF content: {str(e)}")
        
        return chunks
    
    def _split_text_into_chunks(self, text: str, page_num: int, max_chunk_size: int = 1000) -> List[str]:
        """Split text into smaller chunks if needed."""
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence) + 2  # +2 for '. '
            
            if current_size + sentence_size <= max_chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_size
            else:
                if current_chunk:
                    chunks.append('. '.join(current_chunk) + '.')
                current_chunk = [sentence]
                current_size = sentence_size
        
        if current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
        
        return chunks
    
    def get_pdf_list(self, skip: int = 0, limit: int = 100) -> List[PDF]:
        """Get list of PDFs with pagination."""
        return self.pdf_repo.get_multi(skip=skip, limit=limit, order_by="created_at", order_desc=True)
    
    def get_pdf_detail(self, pdf_id: int) -> Optional[PDF]:
        """Get PDF with chunks."""
        return self.pdf_repo.get_with_chunks(pdf_id)
    
    def get_pdf_chunks(self, pdf_id: int, skip: int = 0, limit: int = 20) -> List[PDFChunk]:
        """Get PDF chunks with pagination."""
        return self.chunk_repo.get_by_pdf(pdf_id, skip=skip, limit=limit)
    
    def search_pdf_content(self, search_term: str, pdf_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> List[PDFChunk]:
        """Search PDF content."""
        if pdf_id:
            return self.chunk_repo.search_content(pdf_id, search_term, skip=skip, limit=limit)
        else:
            # Search across all PDFs (without user filtering)
            return self.chunk_repo.search_all_content(search_term, skip=skip, limit=limit)
    
    def count_search_results(self, search_term: str, pdf_id: Optional[int] = None) -> int:
        """Count search results."""
        if pdf_id:
            return self.chunk_repo.count_search_content(search_term, pdf_id)
        else:
            return self.chunk_repo.count_search_all_content(search_term)
    
    def delete_pdf(self, pdf_id: int) -> bool:
        """Delete PDF and its chunks."""
        pdf = self.pdf_repo.get(pdf_id)
        if not pdf:
            return False
        
        # Delete file if it exists
        if pdf.file_path and os.path.exists(pdf.file_path):
            os.unlink(pdf.file_path)
        
        # Delete from database (chunks will be deleted via cascade)
        self.pdf_repo.delete(pdf_id)
        return True
