import base64
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.core.constants import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    ERROR_TOKEN_INVALID,
)
from app.database import get_db
from app.models.users import User

# Password hashing context
pwd_context = CryptContext(schemes=["sha256_crypt", "md5_crypt", "des_crypt"])

# HTTP Bearer token scheme
security_scheme = HTTPBearer()


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # hash = hash_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token with the provided data."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": TOKEN_TYPE_ACCESS,
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token with the provided data."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": TOKEN_TYPE_REFRESH,
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_TOKEN_INVALID
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user from JWT token."""
    from app.crud.user import UserCRUD

    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        
        # Verify token type
        token_type = payload.get("type")
        if token_type != TOKEN_TYPE_ACCESS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_TOKEN_INVALID
            )
        
        # Extract user ID from token
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_TOKEN_INVALID
            )
        
        # Get user from database
        user = UserCRUD.get_user(db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_TOKEN_INVALID
            )
        
        return user
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_TOKEN_INVALID
        )
