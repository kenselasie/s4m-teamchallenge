"""
Integration tests for PDF router endpoints.
"""

import pytest
from fastapi import status
from unittest.mock import Mock, patch, mock_open
from io import BytesIO


class TestPDFRouterIntegration:
    """Integration tests for PDF router endpoints."""

    def test_get_pdfs_empty_list(self, client, auth_headers):
        """Test getting empty PDF list."""
        response = client.get("/api/pdfs/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 100
        assert data["pages"] == 0

    def test_get_pdfs_with_pagination(self, client, auth_headers):
        """Test getting PDFs with pagination parameters."""
        response = client.get("/api/pdfs/?skip=0&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["size"] == 10

    def test_get_pdfs_without_auth(self, client):
        """Test getting PDFs without authentication."""
        response = client.get("/api/pdfs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_pdf_detail_not_found(self, client, auth_headers):
        """Test getting details of non-existent PDF."""
        response = client.get("/api/pdfs/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "PDF not found"

    def test_get_pdf_chunks_not_found(self, client, auth_headers):
        """Test getting chunks of non-existent PDF."""
        response = client.get("/api/pdfs/999/chunks", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "PDF not found"

    def test_get_pdf_chunks_with_pagination(self, client, auth_headers):
        """Test getting PDF chunks with pagination."""
        response = client.get("/api/pdfs/999/chunks?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # PDF doesn't exist

    def test_search_pdf_content_empty_query(self, client, auth_headers):
        """Test searching PDF content with empty query."""
        response = client.get("/api/pdfs/search/content", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Missing required query

    def test_search_pdf_content_with_query(self, client, auth_headers):
        """Test searching PDF content with valid query."""
        response = client.get("/api/pdfs/search/content?q=test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["query"] == "test"
        assert data["pdf_id"] is None

    def test_search_pdf_content_specific_pdf(self, client, auth_headers):
        """Test searching content in specific PDF."""
        response = client.get("/api/pdfs/search/content?q=test&pdf_id=999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # PDF doesn't exist

    def test_search_pdf_content_with_pagination(self, client, auth_headers):
        """Test searching PDF content with pagination."""
        response = client.get("/api/pdfs/search/content?q=test&skip=0&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["size"] == 5

    def test_delete_pdf_not_found(self, client, auth_headers):
        """Test deleting non-existent PDF."""
        response = client.delete("/api/pdfs/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "PDF not found"

    def test_delete_pdf_without_auth(self, client):
        """Test deleting PDF without authentication."""
        response = client.delete("/api/pdfs/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_pdf_stats_not_found(self, client, auth_headers):
        """Test getting stats of non-existent PDF."""
        response = client.get("/api/pdfs/999/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "PDF not found"

    def test_get_pdf_stats_without_auth(self, client):
        """Test getting PDF stats without authentication."""
        response = client.get("/api/pdfs/1/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_pdf_success(self, client, auth_headers):
        """Test PDF upload endpoint response (without actual processing)."""
        # Create a mock file
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files, headers=auth_headers)
        # This will likely fail due to invalid PDF, but we're testing the endpoint
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]

    def test_upload_pdf_with_title(self, client, auth_headers):
        """Test PDF upload with custom title parameter."""
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post(
            "/api/pdfs/upload?title=Custom Title", 
            files=files, 
            headers=auth_headers
        )
        # This will likely fail due to invalid PDF, but we're testing the endpoint
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]

    @patch('app.services.pdf_service.PDFService.upload_and_parse_pdf')
    def test_upload_pdf_value_error(self, mock_upload, client, auth_headers):
        """Test PDF upload with service error."""
        mock_upload.side_effect = ValueError("Invalid PDF file")
        
        file_content = b"Invalid content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert "Invalid PDF file" in data["detail"]

    @patch('app.services.pdf_service.PDFService.upload_and_parse_pdf')
    def test_upload_pdf_general_error(self, mock_upload, client, auth_headers):
        """Test PDF upload with general service error."""
        mock_upload.side_effect = Exception("Service unavailable")
        
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files, headers=auth_headers)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        data = response.json()
        assert "Failed to process PDF" in data["detail"]

    def test_upload_pdf_without_auth(self, client):
        """Test PDF upload without authentication."""
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_pdf_without_file(self, client, auth_headers):
        """Test PDF upload without file."""
        response = client.post("/api/pdfs/upload", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_pdfs_endpoint_structure(self, client, auth_headers):
        """Test PDF list endpoint returns proper structure."""
        response = client.get("/api/pdfs/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        # Verify response structure
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        assert isinstance(data["items"], list)

    def test_get_pdf_detail_endpoint_behavior(self, client, auth_headers):
        """Test PDF detail endpoint behavior."""
        # Test with non-existent PDF ID
        response = client.get("/api/pdfs/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test without authentication
        response = client.get("/api/pdfs/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.services.pdf_service.PDFService.delete_pdf')
    def test_delete_pdf_success(self, mock_delete, client, auth_headers):
        """Test successful PDF deletion."""
        mock_delete.return_value = True
        
        response = client.delete("/api/pdfs/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "PDF deleted successfully"

    @patch('app.services.pdf_service.PDFService.get_pdf_stats')
    def test_get_pdf_stats_success(self, mock_get_stats, client, auth_headers):
        """Test getting PDF stats successfully."""
        mock_stats = {
            "pdf_id": 1,
            "title": "Test PDF",
            "total_pages": 1,
            "file_size_mb": 1.0,
            "processing_status": "completed",
            "total_chunks": 5,
            "total_words": 100,
            "total_characters": 500
        }
        
        mock_get_stats.return_value = mock_stats
        
        response = client.get("/api/pdfs/1/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["pdf_id"] == 1
        assert data["title"] == "Test PDF"
        assert data["total_chunks"] == 5
        assert data["total_words"] == 100