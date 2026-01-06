from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from app.core.settings import settings


class UserRegister(BaseModel):
    """Schema for user registration."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=settings.PASSWORD_MIN_LENGTH)
    phone: Optional[str] = Field(None, max_length=20)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < settings.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters long")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
