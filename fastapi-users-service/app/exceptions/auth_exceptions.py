from fastapi import HTTPException, status
from app.core.constants import (
    ERROR_INVALID_CREDENTIALS,
    ERROR_USER_INACTIVE,
    ERROR_TOKEN_INVALID,
    ERROR_REFRESH_TOKEN_INVALID,
)


class InvalidCredentialsException(HTTPException):
    """Raised when user credentials are invalid."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_INVALID_CREDENTIALS
        )


class InactiveUserException(HTTPException):
    """Raised when user account is inactive."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_USER_INACTIVE
        )


class InvalidTokenException(HTTPException):
    """Raised when token is invalid or expired."""
    def __init__(self, detail: str = ERROR_TOKEN_INVALID):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class InvalidRefreshTokenException(HTTPException):
    """Raised when refresh token is invalid or expired."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_REFRESH_TOKEN_INVALID
        )
