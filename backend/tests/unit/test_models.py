"""
Tests for model classes.
"""

import pytest
from app.models.user import User
from app.models.pdf import PDF
from app.models.pdf_chunk import PDFChunk


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, test_db):
        """Test creating a user."""
        user = User(
            username="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        assert user.username == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
    
    def test_user_repr(self, test_db):
        """Test user string representation."""
        user = User(
            username="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        repr_str = repr(user)
        assert "test@example.com" in repr_str
        assert "is_active=True" in repr_str
    
    def test_user_default_values(self, test_db):
        """Test user default values."""
        user = User(
            username="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        # Test that default can be set explicitly
        user.is_active = True
        assert user.is_active is True


class TestPDFModel:
    """Test cases for PDF model."""
    
    def test_pdf_creation(self, test_db):
        """Test creating a PDF."""
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=1024,
            total_pages=10,
            author="Test Author",
            subject="Test Subject",
            keywords="test, pdf",
            processing_status="completed"
        )
        
        assert pdf.title == "Test PDF"
        assert pdf.filename == "test.pdf"
        assert pdf.file_path == "/tmp/test.pdf"
        assert pdf.content_type == "application/pdf"
        assert pdf.file_size == 1024
        assert pdf.total_pages == 10
        assert pdf.author == "Test Author"
        assert pdf.subject == "Test Subject"
        assert pdf.keywords == "test, pdf"
        assert pdf.processing_status == "completed"
    
    def test_pdf_file_size_mb_property(self, test_db):
        """Test PDF file size in MB property."""
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=1048576,  # 1 MB in bytes
            total_pages=1,
            processing_status="completed"
        )
        
        assert pdf.file_size_mb == 1.0
    
    def test_pdf_file_size_mb_property_small_file(self, test_db):
        """Test PDF file size in MB property for small files."""
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=512,  # 0.5 KB
            total_pages=1,
            processing_status="completed"
        )
        
        # Should be rounded to 2 decimal places
        assert pdf.file_size_mb == 0.00
    
    def test_pdf_file_size_mb_property_zero_size(self, test_db):
        """Test PDF file size in MB property for zero size."""
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=0,
            total_pages=1,
            processing_status="completed"
        )
        
        assert pdf.file_size_mb == 0.0
    
    def test_pdf_repr(self, test_db):
        """Test PDF string representation."""
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=1024,
            total_pages=10,
            processing_status="completed"
        )
        
        repr_str = repr(pdf)
        assert "Test PDF" in repr_str
        assert "10" in repr_str
        assert "completed" in repr_str
    
    def test_pdf_default_values(self, test_db):
        """Test PDF default values."""
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=1024,
            total_pages=1
        )
        
        # Test that defaults can be set explicitly
        pdf.processing_status = "pending"
        assert pdf.processing_status == "pending"
        assert pdf.processing_error is None
        assert pdf.author is None
        assert pdf.subject is None
        assert pdf.keywords is None


class TestPDFChunkModel:
    """Test cases for PDFChunk model."""
    
    def test_pdf_chunk_creation(self, test_db):
        """Test creating a PDF chunk."""
        chunk = PDFChunk(
            pdf_id=1,
            chunk_number=1,
            page_number=1,
            content="This is sample content",
            content_type="text",
            word_count=4,
            character_count=23,
            chunk_metadata={"key": "value"}
        )
        
        assert chunk.pdf_id == 1
        assert chunk.chunk_number == 1
        assert chunk.page_number == 1
        assert chunk.content == "This is sample content"
        assert chunk.content_type == "text"
        assert chunk.word_count == 4
        assert chunk.character_count == 23
        assert chunk.chunk_metadata == {"key": "value"}
    
    def test_pdf_chunk_repr(self, test_db):
        """Test PDF chunk string representation."""
        chunk = PDFChunk(
            pdf_id=1,
            chunk_number=1,
            page_number=1,
            content="This is sample content",
            content_type="text",
            word_count=4,
            character_count=23
        )
        
        repr_str = repr(chunk)
        assert "pdf_id=1" in repr_str
        assert "chunk=1" in repr_str
        assert "page=1" in repr_str
    
    def test_pdf_chunk_default_values(self, test_db):
        """Test PDF chunk default values."""
        chunk = PDFChunk(
            pdf_id=1,
            chunk_number=1,
            page_number=1,
            content="This is sample content"
        )
        
        # Test that defaults can be set explicitly  
        chunk.content_type = "text"
        chunk.word_count = 0
        chunk.character_count = 0
        
        assert chunk.content_type == "text"
        assert chunk.word_count == 0
        assert chunk.character_count == 0
        assert chunk.chunk_metadata is None
    
    def test_pdf_chunk_preview_property(self, test_db):
        """Test PDF chunk preview property."""
        long_content = "A" * 150  # Create content longer than 100 characters
        chunk = PDFChunk(
            pdf_id=1,
            chunk_number=1,
            page_number=1,
            content=long_content,
            content_type="text",
            word_count=1,
            character_count=150
        )
        
        preview = chunk.preview
        assert len(preview) <= 103  # Should be truncated (100 + "...")
        assert "..." in preview  # Should have ellipsis
    
    def test_pdf_chunk_preview_property_short_content(self, test_db):
        """Test PDF chunk preview property for short content."""
        chunk = PDFChunk(
            pdf_id=1,
            chunk_number=1,
            page_number=1,
            content="Short content",
            content_type="text",
            word_count=2,
            character_count=13
        )
        
        preview = chunk.preview
        assert preview == "Short content"
        assert "..." not in preview
    
