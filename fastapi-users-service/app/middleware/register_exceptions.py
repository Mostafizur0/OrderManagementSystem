from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.auth_exceptions import InvalidCredentialsException, InvalidRefreshTokenException, InvalidTokenException
from app.exceptions.custom_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    DatabaseException,
)
from app.utils.logger import setup_logger
logger = setup_logger(
    name="fastapi-users-service", log_level="INFO", log_file="logs/app.log"
)


class RegisterExceptionsMiddleware:
    def __init__(self, app):
        self.app = app
        self.register_exception_handlers()

    def register_exception_handlers(self):
        """Register all exception handlers with the FastAPI app"""
        self.app.add_exception_handler(
            UserNotFoundException, self.user_not_found_exception_handler
        )
        self.app.add_exception_handler(
            UserAlreadyExistsException,
            self.user_already_exists_exception_handler,
        )
        self.app.add_exception_handler(
            DatabaseException, self.database_exception_handler
        )
        self.app.add_exception_handler(
            InvalidCredentialsException, self.invalid_credentials_exception_handler
        )
        self.app.add_exception_handler(
            InvalidTokenException, self.invalid_token_exception_handler
        )
        self.app.add_exception_handler(
            InvalidRefreshTokenException, self.invalid_refresh_token_exception_handler
        )

    async def user_not_found_exception_handler(
        self, request: Request, exc: UserNotFoundException
    ):
        logger.warning(f"User not found: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )

    async def user_already_exists_exception_handler(
        self, request: Request, exc: UserAlreadyExistsException
    ):
        logger.warning(f"User already exists: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )

    async def database_exception_handler(
        self, request: Request, exc: DatabaseException
    ):
        logger.error(f"Database error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )

    async def invalid_credentials_exception_handler(
        self, request: Request, exc: InvalidCredentialsException
    ):
        logger.warning(f"Invalid credentials: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )

    async def invalid_token_exception_handler(
        self, request: Request, exc: InvalidTokenException
    ):
        logger.warning(f"Invalid token: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )

    async def invalid_refresh_token_exception_handler(
        self, request: Request, exc: InvalidRefreshTokenException
    ):
        logger.warning(f"Invalid refresh token: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}
        )
