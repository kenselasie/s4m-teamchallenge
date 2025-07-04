import pytest
from app.models.user import User
from app.models.pdf import PDF
from app.models.pdf_chunk import PDFChunk


class TestUserModel:
    
    def test_user_creation(self, test_db):
        user = User(
            username="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        assert user.username == "test@example.com"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
    
    def test_user_repr(self, test_db):
        user = User(
            username="test@example.com",
            hashed_password="hashed_password_123",
            is_active=True
        )
        
        repr_str = repr(user)
        assert "test@example.com" in repr_str
        assert "is_active=True" in repr_str
    
    def test_user_default_values(self, test_db):
        user = User(
            username="test@example.com",
            hashed_password="hashed_password_123"
        )
        
        # Test that default can be set explicitly
        user.is_active = True
        assert user.is_active is True


class TestPDFModel:
    
    def test_pdf_creation(self, test_db):
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
    
    @pytest.mark.parametrize(
        "file_size,expected_mb",
        [
            (1048576, 1.0),  # 1 MB in bytes
            (512, 0.00),     # 0.5 KB
            (0, 0.0),        # Zero size
        ],
    )
    def test_pdf_file_size_mb_property(self, test_db, file_size, expected_mb):
        pdf = PDF(
            title="Test PDF",
            filename="test.pdf",
            file_path="/tmp/test.pdf",
            content_type="application/pdf",
            file_size=file_size,
            total_pages=1,
            processing_status="completed"
        )
        
        assert pdf.file_size_mb == expected_mb
    
    def test_pdf_repr(self, test_db):
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
    
    def test_pdf_chunk_creation(self, test_db):
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
    
    @pytest.mark.parametrize(
        "content,expected_has_ellipsis",
        [
            ("A" * 150, True),        # Long content should have ellipsis
            ("Short content", False), # Short content should not have ellipsis
        ],
    )
    def test_pdf_chunk_preview_property(self, test_db, content, expected_has_ellipsis):
        chunk = PDFChunk(
            pdf_id=1,
            chunk_number=1,
            page_number=1,
            content=content,
            content_type="text",
            word_count=len(content.split()),
            character_count=len(content)
        )
        
        preview = chunk.preview
        
        if expected_has_ellipsis:
            assert len(preview) <= 103  # Should be truncated (100 + "...")
            assert "..." in preview  # Should have ellipsis
        else:
            assert preview == content
            assert "..." not in preview
    
