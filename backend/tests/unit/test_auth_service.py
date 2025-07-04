import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta, timezone
from app.services.auth_service import AuthService


class TestAuthService:

    def test_init(self, test_db):
        service = AuthService(test_db)
        assert service.db == test_db
        assert service.user_repo is not None

    @pytest.mark.parametrize(
        "plain_password,hashed_password,mock_return,expected",
        [
            ("plain_password", "hashed_password", True, True),
            ("wrong_password", "hashed_password", False, False),
        ],
    )
    def test_verify_password(
        self, test_db, plain_password, hashed_password, mock_return, expected
    ):
        service = AuthService(test_db)

        with patch("app.services.auth_service.pwd_context.verify") as mock_verify:
            mock_verify.return_value = mock_return

            result = service.verify_password(plain_password, hashed_password)

            assert result is expected
            mock_verify.assert_called_once_with(plain_password, hashed_password)

    def test_get_password_hash(self, test_db):
        service = AuthService(test_db)

        with patch("app.services.auth_service.pwd_context.hash") as mock_hash:
            mock_hash.return_value = "hashed_password_123"

            result = service.get_password_hash("plain_password")

            assert result == "hashed_password_123"
            mock_hash.assert_called_once_with("plain_password")

    @pytest.mark.parametrize(
        "username,password,user_found,password_valid,expected_result",
        [
            ("test@example.com", "plain_password", True, True, "user_object"),
            ("nonexistent@example.com", "password", False, False, None),
            ("test@example.com", "wrong_password", True, False, None),
        ],
    )
    def test_authenticate_user(
        self, test_db, username, password, user_found, password_valid, expected_result
    ):
        service = AuthService(test_db)

        mock_user = Mock()
        mock_user.hashed_password = "hashed_password_123"

        with patch.object(
            service.user_repo, "get_active_user_by_username"
        ) as mock_get_user, patch.object(service, "verify_password") as mock_verify:

            mock_get_user.return_value = mock_user if user_found else None
            mock_verify.return_value = password_valid

            result = service.authenticate_user(username, password)

            if expected_result == "user_object":
                assert result == mock_user
                mock_verify.assert_called_once_with(password, "hashed_password_123")
            else:
                assert result is None
                if user_found:
                    mock_verify.assert_called_once_with(password, "hashed_password_123")
                else:
                    mock_verify.assert_not_called()

            mock_get_user.assert_called_once_with(username)

    @pytest.mark.parametrize(
        "expires_delta,expected_expiry_minutes",
        [
            (timedelta(minutes=60), 60),
            (None, 30),
        ],
    )
    def test_create_access_token(self, test_db, expires_delta, expected_expiry_minutes):
        service = AuthService(test_db)

        data = {"sub": "test@example.com"}

        with patch("app.services.auth_service.jwt.encode") as mock_encode, patch(
            "app.services.auth_service.datetime"
        ) as mock_datetime:

            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_encode.return_value = "encoded_token"

            if expires_delta:
                result = service.create_access_token(data, expires_delta)
            else:
                result = service.create_access_token(data)

            assert result == "encoded_token"
            # Check that encode was called with correct expiry
            call_args = mock_encode.call_args[0]
            assert call_args[0]["sub"] == "test@example.com"
            expected_expiry = mock_now + timedelta(minutes=expected_expiry_minutes)
            assert call_args[0]["exp"] == expected_expiry

    @pytest.mark.parametrize(
        "token,decode_return,decode_side_effect,expected_result",
        [
            ("valid_token", {"sub": "test@example.com"}, None, "test@example.com"),
            ("invalid_token", None, "JWTError", None),
            ("token_without_sub", {"exp": 1234567890}, None, None),
        ],
    )
    def test_verify_token(
        self, test_db, token, decode_return, decode_side_effect, expected_result
    ):
        service = AuthService(test_db)

        with patch("app.services.auth_service.jwt.decode") as mock_decode:
            if decode_side_effect == "JWTError":
                from jose import JWTError

                mock_decode.side_effect = JWTError("Invalid token")
            else:
                mock_decode.return_value = decode_return

            result = service.verify_token(token)

            assert result == expected_result

            if decode_side_effect != "JWTError":
                mock_decode.assert_called_once_with(
                    token, "your-secret-key-for-development", algorithms=["HS256"]
                )

    @pytest.mark.parametrize(
        "token,verify_return,user_found,expected_result",
        [
            ("valid_token", "test@example.com", True, "user_object"),
            ("invalid_token", None, False, None),
            ("valid_token", "nonexistent@example.com", False, None),
        ],
    )
    def test_get_current_user(
        self, test_db, token, verify_return, user_found, expected_result
    ):
        service = AuthService(test_db)

        mock_user = Mock()

        with patch.object(service, "verify_token") as mock_verify, patch.object(
            service.user_repo, "get_active_user_by_username"
        ) as mock_get_user:

            mock_verify.return_value = verify_return
            mock_get_user.return_value = mock_user if user_found else None

            result = service.get_current_user(token)

            if expected_result == "user_object":
                assert result == mock_user
                mock_get_user.assert_called_once_with(verify_return)
            else:
                assert result is None
                if verify_return:
                    mock_get_user.assert_called_once_with(verify_return)
                else:
                    mock_get_user.assert_not_called()

            mock_verify.assert_called_once_with(token)

    @pytest.mark.parametrize(
        "user_exists,expected_result",
        [
            (False, "new_user"),
            (True, "existing_user"),
        ],
    )
    def test_create_demo_user(self, test_db, user_exists, expected_result):
        service = AuthService(test_db)

        mock_existing_user = Mock()
        mock_new_user = Mock()

        with patch.object(
            service.user_repo, "get_by_username"
        ) as mock_get_existing, patch.object(
            service, "get_password_hash"
        ) as mock_hash, patch.object(
            service.user_repo, "create"
        ) as mock_create:

            mock_get_existing.return_value = mock_existing_user if user_exists else None
            mock_hash.return_value = "hashed_demo123"
            mock_create.return_value = mock_new_user

            result = service.create_demo_user()

            mock_get_existing.assert_called_once_with("demo@example.com")

            if expected_result == "new_user":
                assert result == mock_new_user
                mock_hash.assert_called_once_with("demo123")
                mock_create.assert_called_once_with(
                    {
                        "username": "demo@example.com",
                        "hashed_password": "hashed_demo123",
                        "is_active": True,
                    }
                )
            else:
                assert result == mock_existing_user
                mock_hash.assert_not_called()
                mock_create.assert_not_called()
