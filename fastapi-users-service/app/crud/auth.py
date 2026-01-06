from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.core.settings import settings


class RefreshTokenCRUD:
    """CRUD operations for refresh tokens."""
    
    @staticmethod
    def create_refresh_token(
        db: Session,
        user_id: int,
        token: str
    ) -> RefreshToken:
        """Create a new refresh token."""
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    
    @staticmethod
    def get_refresh_token(
        db: Session,
        token: str
    ) -> Optional[RefreshToken]:
        """Get a refresh token by token string."""
        return db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False
        ).first()
    
    @staticmethod
    def revoke_refresh_token(
        db: Session,
        token: str
    ) -> bool:
        """Revoke a refresh token."""
        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def revoke_all_user_tokens(
        db: Session,
        user_id: int
    ) -> int:
        """Revoke all refresh tokens for a user."""
        count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        db.commit()
        return count
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Delete expired refresh tokens."""
        count = db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        ).delete()
        db.commit()
        return count
