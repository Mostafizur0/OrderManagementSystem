import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request details
        self.logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {client_ip} - User-Agent: {request.headers.get('user-agent', 'unknown')}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            self.logger.info(
                f"Response: {response.status_code} "
                f"for {request.method} {request.url.path} "
                f"took {process_time:.4f}s"
            )
            
            # Add processing time to response headers
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self.logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)} "
                f"took {process_time:.4f}s"
            )
            raise 