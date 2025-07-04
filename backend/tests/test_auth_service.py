"""
Tests for authentication service.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from app.services.auth_service import AuthService


class TestAuthService:
    """Test cases for authentication service."""
    
    def test_init(self, test_db):
        """Test AuthService initialization."""
        service = AuthService(test_db)
        assert service.db == test_db
        assert service.user_repo is not None
    
    def test_verify_password_correct(self, test_db):
        """Test password verification with correct password."""
        service = AuthService(test_db)
        
        with patch('app.services.auth_service.pwd_context.verify') as mock_verify:
            mock_verify.return_value = True
            
            result = service.verify_password("plain_password", "hashed_password")
            
            assert result is True
            mock_verify.assert_called_once_with("plain_password", "hashed_password")
    
    def test_verify_password_incorrect(self, test_db):
        """Test password verification with incorrect password."""
        service = AuthService(test_db)
        
        with patch('app.services.auth_service.pwd_context.verify') as mock_verify:
            mock_verify.return_value = False
            
            result = service.verify_password("wrong_password", "hashed_password")
            
            assert result is False
    
    def test_get_password_hash(self, test_db):
        """Test password hashing."""
        service = AuthService(test_db)
        
        with patch('app.services.auth_service.pwd_context.hash') as mock_hash:
            mock_hash.return_value = "hashed_password_123"
            
            result = service.get_password_hash("plain_password")
            
            assert result == "hashed_password_123"
            mock_hash.assert_called_once_with("plain_password")
    
    def test_authenticate_user_success(self, test_db):
        """Test successful user authentication."""
        service = AuthService(test_db)
        
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password_123"
        
        with patch.object(service.user_repo, 'get_active_user_by_username') as mock_get_user, \
             patch.object(service, 'verify_password') as mock_verify:
            
            mock_get_user.return_value = mock_user
            mock_verify.return_value = True
            
            result = service.authenticate_user("test@example.com", "plain_password")
            
            assert result == mock_user
            mock_get_user.assert_called_once_with("test@example.com")
            mock_verify.assert_called_once_with("plain_password", "hashed_password_123")
    
    def test_authenticate_user_not_found(self, test_db):
        """Test authentication with non-existent user."""
        service = AuthService(test_db)
        
        with patch.object(service.user_repo, 'get_active_user_by_username') as mock_get_user:
            mock_get_user.return_value = None
            
            result = service.authenticate_user("nonexistent@example.com", "password")
            
            assert result is None
    
    def test_authenticate_user_wrong_password(self, test_db):
        """Test authentication with wrong password."""
        service = AuthService(test_db)
        
        mock_user = Mock()
        mock_user.hashed_password = "hashed_password_123"
        
        with patch.object(service.user_repo, 'get_active_user_by_username') as mock_get_user, \
             patch.object(service, 'verify_password') as mock_verify:
            
            mock_get_user.return_value = mock_user
            mock_verify.return_value = False
            
            result = service.authenticate_user("test@example.com", "wrong_password")
            
            assert result is None
    
    def test_create_access_token_with_expiry(self, test_db):
        """Test creating access token with custom expiry."""
        service = AuthService(test_db)
        
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        
        with patch('app.services.auth_service.jwt.encode') as mock_encode, \
             patch('app.services.auth_service.datetime') as mock_datetime:
            
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_encode.return_value = "encoded_token"
            
            result = service.create_access_token(data, expires_delta)
            
            assert result == "encoded_token"
            # Check that encode was called with correct expiry
            call_args = mock_encode.call_args[0]
            assert call_args[0]["sub"] == "test@example.com"
            assert call_args[0]["exp"] == mock_now + expires_delta
    
    def test_create_access_token_default_expiry(self, test_db):
        """Test creating access token with default expiry."""
        service = AuthService(test_db)
        
        data = {"sub": "test@example.com"}
        
        with patch('app.services.auth_service.jwt.encode') as mock_encode, \
             patch('app.services.auth_service.datetime') as mock_datetime:
            
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_encode.return_value = "encoded_token"
            
            result = service.create_access_token(data)
            
            assert result == "encoded_token"
            # Check that encode was called with default expiry
            call_args = mock_encode.call_args[0]
            expected_expiry = mock_now + timedelta(minutes=30)
            assert call_args[0]["exp"] == expected_expiry
    
    def test_verify_token_success(self, test_db):
        """Test successful token verification."""
        service = AuthService(test_db)
        
        with patch('app.services.auth_service.jwt.decode') as mock_decode:
            mock_decode.return_value = {"sub": "test@example.com"}
            
            result = service.verify_token("valid_token")
            
            assert result == "test@example.com"
            mock_decode.assert_called_once_with(
                "valid_token", 
                "your-secret-key-for-development", 
                algorithms=["HS256"]
            )
    
    def test_verify_token_invalid_token(self, test_db):
        """Test token verification with invalid token."""
        service = AuthService(test_db)
        
        with patch('app.services.auth_service.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Invalid token")
            
            result = service.verify_token("invalid_token")
            
            assert result is None
    
    def test_verify_token_no_subject(self, test_db):
        """Test token verification with no subject in payload."""
        service = AuthService(test_db)
        
        with patch('app.services.auth_service.jwt.decode') as mock_decode:
            mock_decode.return_value = {"exp": 1234567890}  # No 'sub' field
            
            result = service.verify_token("token_without_sub")
            
            assert result is None
    
    def test_get_current_user_success(self, test_db):
        """Test getting current user from token."""
        service = AuthService(test_db)
        
        mock_user = Mock()
        
        with patch.object(service, 'verify_token') as mock_verify, \
             patch.object(service.user_repo, 'get_active_user_by_username') as mock_get_user:
            
            mock_verify.return_value = "test@example.com"
            mock_get_user.return_value = mock_user
            
            result = service.get_current_user("valid_token")
            
            assert result == mock_user
            mock_verify.assert_called_once_with("valid_token")
            mock_get_user.assert_called_once_with("test@example.com")
    
    def test_get_current_user_invalid_token(self, test_db):
        """Test getting current user with invalid token."""
        service = AuthService(test_db)
        
        with patch.object(service, 'verify_token') as mock_verify:
            mock_verify.return_value = None
            
            result = service.get_current_user("invalid_token")
            
            assert result is None
    
    def test_get_current_user_user_not_found(self, test_db):
        """Test getting current user when user doesn't exist."""
        service = AuthService(test_db)
        
        with patch.object(service, 'verify_token') as mock_verify, \
             patch.object(service.user_repo, 'get_active_user_by_username') as mock_get_user:
            
            mock_verify.return_value = "nonexistent@example.com"
            mock_get_user.return_value = None
            
            result = service.get_current_user("valid_token")
            
            assert result is None
    
    def test_create_demo_user_new_user(self, test_db):
        """Test creating demo user when user doesn't exist."""
        service = AuthService(test_db)
        
        mock_user = Mock()
        
        with patch.object(service.user_repo, 'get_by_username') as mock_get_existing, \
             patch.object(service, 'get_password_hash') as mock_hash, \
             patch.object(service.user_repo, 'create') as mock_create:
            
            mock_get_existing.return_value = None  # User doesn't exist
            mock_hash.return_value = "hashed_demo123"
            mock_create.return_value = mock_user
            
            result = service.create_demo_user()
            
            assert result == mock_user
            mock_get_existing.assert_called_once_with("demo@example.com")
            mock_hash.assert_called_once_with("demo123")
            mock_create.assert_called_once_with({
                "username": "demo@example.com",
                "hashed_password": "hashed_demo123",
                "is_active": True
            })
    
    def test_create_demo_user_existing_user(self, test_db):
        """Test creating demo user when user already exists."""
        service = AuthService(test_db)
        
        mock_existing_user = Mock()
        
        with patch.object(service.user_repo, 'get_by_username') as mock_get_existing:
            mock_get_existing.return_value = mock_existing_user
            
            result = service.create_demo_user()
            
            assert result == mock_existing_user
            mock_get_existing.assert_called_once_with("demo@example.com")