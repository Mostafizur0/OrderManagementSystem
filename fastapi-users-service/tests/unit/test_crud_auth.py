"""
Unit tests for RefreshTokenCRUD operations.
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.crud.auth import RefreshTokenCRUD
from app.models.refresh_token import RefreshToken


@pytest.mark.unit
class TestRefreshTokenCRUD:
    """Test cases for RefreshTokenCRUD class."""

    def test_create_refresh_token(self, db_session: Session, test_user):
        """Test creating a new refresh token."""
        token = "test-refresh-token-12345"
        
        db_token = RefreshTokenCRUD.create_refresh_token(
            db_session, test_user.id, token
        )
        
        assert db_token is not None
        assert db_token.token == token
        assert db_token.user_id == test_user.id
        assert db_token.is_revoked is False
        assert db_token.expires_at is not None

    def test_get_refresh_token(self, db_session: Session, test_user):
        """Test retrieving a refresh token."""
        token = "test-refresh-token-retrieve"
        RefreshTokenCRUD.create_refresh_token(db_session, test_user.id, token)
        
        db_token = RefreshTokenCRUD.get_refresh_token(db_session, token)
        
        assert db_token is not None
        assert db_token.token == token

    def test_get_refresh_token_not_found(self, db_session: Session):
        """Test getting a non-existent refresh token returns None."""
        db_token = RefreshTokenCRUD.get_refresh_token(
            db_session, "nonexistent-token"
        )
        
        assert db_token is None

    def test_get_revoked_token_returns_none(
        self, db_session: Session, test_user
    ):
        """Test that revoked tokens are not returned."""
        token = "test-revoked-token"
        RefreshTokenCRUD.create_refresh_token(db_session, test_user.id, token)
        RefreshTokenCRUD.revoke_refresh_token(db_session, token)
        
        db_token = RefreshTokenCRUD.get_refresh_token(db_session, token)
        
        assert db_token is None

    def test_revoke_refresh_token(self, db_session: Session, test_user):
        """Test revoking a refresh token."""
        token = "test-token-to-revoke"
        RefreshTokenCRUD.create_refresh_token(db_session, test_user.id, token)
        
        result = RefreshTokenCRUD.revoke_refresh_token(db_session, token)
        
        assert result is True
        # Verify the token is revoked
        revoked_token = (
            db_session.query(RefreshToken)
            .filter(RefreshToken.token == token)
            .first()
        )
        assert revoked_token.is_revoked is True

    def test_revoke_nonexistent_token(self, db_session: Session):
        """Test revoking a non-existent token returns False."""
        result = RefreshTokenCRUD.revoke_refresh_token(
            db_session, "nonexistent-token"
        )
        
        assert result is False

    def test_revoke_all_user_tokens(self, db_session: Session, test_user):
        """Test revoking all tokens for a user."""
        # Create multiple tokens
        for i in range(3):
            RefreshTokenCRUD.create_refresh_token(
                db_session, test_user.id, f"token-{i}"
            )
        
        count = RefreshTokenCRUD.revoke_all_user_tokens(db_session, test_user.id)
        
        assert count == 3
        # Verify all tokens are revoked
        for i in range(3):
            db_token = RefreshTokenCRUD.get_refresh_token(
                db_session, f"token-{i}"
            )
            assert db_token is None

    def test_revoke_all_user_tokens_no_tokens(self, db_session: Session, test_user):
        """Test revoking tokens when user has none."""
        count = RefreshTokenCRUD.revoke_all_user_tokens(db_session, test_user.id)
        
        assert count == 0

    def test_cleanup_expired_tokens(self, db_session: Session, test_user):
        """Test cleanup of expired tokens."""
        # Create an expired token manually
        expired_token = RefreshToken(
            user_id=test_user.id,
            token="expired-token",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            is_revoked=False,
        )
        db_session.add(expired_token)
        db_session.commit()
        
        # Create a valid token
        RefreshTokenCRUD.create_refresh_token(
            db_session, test_user.id, "valid-token"
        )
        
        count = RefreshTokenCRUD.cleanup_expired_tokens(db_session)
        
        assert count == 1
        # Verify valid token still exists
        valid = RefreshTokenCRUD.get_refresh_token(db_session, "valid-token")
        assert valid is not None

