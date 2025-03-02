import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all API requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        logger.info(f"Request started: {method} {path} (ID: {request_id})")
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            status_code = response.status_code
            
            logger.info(
                f"Request completed: {method} {path} - Status: {status_code} - "
                f"Duration: {process_time:.3f}s (ID: {request_id})"
            )
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {method} {path} - Error: {str(e)} - "
                f"Duration: {process_time:.3f}s (ID: {request_id})"
            )
            raise

class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for distributed tracing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # This is a simplified implementation
        # In a real application, this would integrate with a tracing system
        if not hasattr(request.state, "request_id"):
            request.state.request_id = str(uuid.uuid4())
            
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
