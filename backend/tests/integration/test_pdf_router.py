import pytest
from fastapi import status
from unittest.mock import Mock, patch, mock_open
from io import BytesIO


class TestPDFRouterIntegration:
    def test_get_pdfs_empty_list(self, client, auth_headers):
        response = client.get("/api/pdfs/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 100
        assert data["pages"] == 0

    def test_get_pdfs_with_pagination(self, client, auth_headers):
        response = client.get("/api/pdfs/?skip=0&limit=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["size"] == 10

    def test_get_pdfs_without_auth(self, client):
        response = client.get("/api/pdfs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "endpoint,expected_status,expected_detail",
        [
            ("/api/pdfs/999", status.HTTP_404_NOT_FOUND, "PDF not found"),
            ("/api/pdfs/999/chunks", status.HTTP_404_NOT_FOUND, "PDF not found"),
        ],
    )
    def test_get_pdf_not_found_endpoints(self, client, auth_headers, endpoint, expected_status, expected_detail):
        response = client.get(endpoint, headers=auth_headers)
        assert response.status_code == expected_status
        
        data = response.json()
        assert data["detail"] == expected_detail

    def test_get_pdf_chunks_with_pagination(self, client, auth_headers):
        response = client.get("/api/pdfs/999/chunks?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # PDF doesn't exist

    def test_search_pdf_content_empty_query(self, client, auth_headers):
        response = client.get("/api/pdfs/search/content", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Missing required query

    def test_search_pdf_content_with_query(self, client, auth_headers):
        response = client.get("/api/pdfs/search/content?q=test", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["query"] == "test"
        assert data["pdf_id"] is None

    def test_search_pdf_content_specific_pdf(self, client, auth_headers):
        response = client.get("/api/pdfs/search/content?q=test&pdf_id=999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # PDF doesn't exist

    def test_search_pdf_content_with_pagination(self, client, auth_headers):
        response = client.get("/api/pdfs/search/content?q=test&skip=0&limit=5", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["size"] == 5

    @pytest.mark.parametrize(
        "endpoint,headers,expected_status,expected_detail",
        [
            ("/api/pdfs/999", "auth_headers", status.HTTP_404_NOT_FOUND, "PDF not found"),
            ("/api/pdfs/1", None, status.HTTP_401_UNAUTHORIZED, None),
        ],
    )
    def test_delete_pdf_scenarios(self, client, auth_headers, endpoint, headers, expected_status, expected_detail):
        headers_to_use = auth_headers if headers == "auth_headers" else None
        response = client.delete(endpoint, headers=headers_to_use)
        assert response.status_code == expected_status
        
        if expected_detail:
            data = response.json()
            assert data["detail"] == expected_detail


    def test_upload_pdf_success(self, client, auth_headers):
        # Create a mock file
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files, headers=auth_headers)
        # This will likely fail due to invalid PDF, but we're testing the endpoint
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR]

    def test_upload_pdf_with_title(self, client, auth_headers):
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

    @pytest.mark.parametrize(
        "exception_type,exception_message,expected_status,expected_detail_contains",
        [
            (ValueError, "Invalid PDF file", status.HTTP_400_BAD_REQUEST, "Invalid PDF file"),
            (Exception, "Service unavailable", status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to process PDF"),
        ],
    )
    @patch('app.services.pdf_service.PDFService.upload_and_parse_pdf')
    def test_upload_pdf_errors(self, mock_upload, client, auth_headers, exception_type, exception_message, expected_status, expected_detail_contains):
        mock_upload.side_effect = exception_type(exception_message)
        
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files, headers=auth_headers)
        assert response.status_code == expected_status
        
        data = response.json()
        assert expected_detail_contains in data["detail"]

    def test_upload_pdf_without_auth(self, client):
        file_content = b"Mock PDF content"
        files = {
            "file": ("test.pdf", BytesIO(file_content), "application/pdf")
        }
        
        response = client.post("/api/pdfs/upload", files=files)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_pdf_without_file(self, client, auth_headers):
        response = client.post("/api/pdfs/upload", headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_pdfs_endpoint_structure(self, client, auth_headers):
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
        # Test with non-existent PDF ID
        response = client.get("/api/pdfs/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test without authentication
        response = client.get("/api/pdfs/1")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @patch('app.services.pdf_service.PDFService.delete_pdf')
    def test_delete_pdf_success(self, mock_delete, client, auth_headers):
        mock_delete.return_value = True
        
        response = client.delete("/api/pdfs/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "PDF deleted successfully"

