"""
Unit tests for security module.
"""
import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from jose import jwt

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.settings import settings
from app.core.constants import TOKEN_TYPE_ACCESS, TOKEN_TYPE_REFRESH


@pytest.mark.unit
class TestPasswordHashing:
    """Test cases for password hashing functions."""

    def test_hash_password_returns_hash(self):
        """Test that hash_password returns a hashed string."""
        password = "testpassword123"
        
        hashed = hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_different_each_time(self):
        """Test that hashing the same password gives different results (salt)."""
        password = "testpassword123"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Different hashes due to random salt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        result = verify_password(password, hashed)
        
        assert result is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)
        
        result = verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_empty(self):
        """Test verifying with empty password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        result = verify_password("", hashed)
        
        assert result is False


@pytest.mark.unit
class TestJWTTokens:
    """Test cases for JWT token functions."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "123", "email": "test@example.com"}
        
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == TOKEN_TYPE_ACCESS

    def test_create_access_token_with_custom_expiry(self):
        """Test creating an access token with custom expiry."""
        data = {"sub": "123"}
        expires = timedelta(minutes=5)
        
        token = create_access_token(data, expires_delta=expires)
        
        assert token is not None
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        assert payload["sub"] == "123"

    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        data = {"sub": "123", "email": "test@example.com"}
        
        token = create_refresh_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Decode and verify
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        assert payload["sub"] == "123"
        assert payload["type"] == TOKEN_TYPE_REFRESH

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"

    def test_decode_invalid_token_raises_exception(self):
        """Test that decoding an invalid token raises HTTPException."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token(invalid_token)
        
        assert exc_info.value.status_code == 401

    def test_decode_expired_token_raises_exception(self):
        """Test that decoding an expired token raises HTTPException."""
        data = {"sub": "123"}
        # Create token with negative expiry (already expired)
        token = create_access_token(data, expires_delta=timedelta(seconds=-10))
        
        with pytest.raises(HTTPException) as exc_info:
            decode_token(token)
        
        assert exc_info.value.status_code == 401

    def test_access_and_refresh_tokens_are_different(self):
        """Test that access and refresh tokens are different."""
        data = {"sub": "123"}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        assert access_token != refresh_token

    def test_token_contains_expiry(self):
        """Test that tokens contain expiry claim."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        
        assert "exp" in payload

