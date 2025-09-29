from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time
from datetime import datetime

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
security = HTTPBearer(auto_error=False)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing information."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = None) -> bool:
    """
    Verify API key from Authorization header.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        bool: True if valid API key, False otherwise
        
    Raises:
        HTTPException: If authentication is required but invalid
    """
    if not credentials:
        return False
        
    # Extract token from credentials
    token = credentials.credentials
    
    # For now, check against configured API keys
    # In production, this should check against a database or key management service
    valid_keys = [
        settings.secret_key,
        settings.openai_api_key,
        settings.github_token
    ]
    
    # Remove None values and empty strings
    valid_keys = [key for key in valid_keys if key and key != "dev-secret-key-change-in-production"]
    
    if token in valid_keys:
        logger.info("Valid API key provided")
        return True
    else:
        logger.warning(f"Invalid API key attempted: {token[:10]}...")
        return False


def require_api_key(credentials: HTTPAuthorizationCredentials = security) -> bool:
    """
    Dependency that requires a valid API key.
    
    Args:
        credentials: HTTP Authorization credentials (injected by FastAPI)
        
    Returns:
        bool: True if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_api_key(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return True


def optional_api_key(credentials: Optional[HTTPAuthorizationCredentials] = security) -> bool:
    """
    Optional API key verification.
    
    Args:
        credentials: HTTP Authorization credentials (injected by FastAPI)
        
    Returns:
        bool: True if valid key provided, False if no key or invalid key
    """
    if not credentials:
        return False
    
    return verify_api_key(credentials)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old entries
        self.clients = {
            ip: requests for ip, requests in self.clients.items()
            if any(timestamp > current_time - self.period for timestamp in requests)
        }
        
        # Check rate limit
        if client_ip in self.clients:
            # Filter recent requests
            recent_requests = [
                timestamp for timestamp in self.clients[client_ip]
                if timestamp > current_time - self.period
            ]
            
            if len(recent_requests) >= self.calls:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again later."
                )
            
            self.clients[client_ip] = recent_requests + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)