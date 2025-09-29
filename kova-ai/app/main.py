from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import uvicorn
from datetime import datetime

from app.api import health, ai_endpoints, webhooks, database_endpoints
from app.core.config import settings
from app.utils.logger import setup_logger, log_error
from app.api.models import ErrorResponseModel
from app.security.middleware import (
    SecurityHeadersMiddleware, 
    RequestLoggingMiddleware, 
    RateLimitMiddleware
)

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Kova AI System - AI-powered development automation platform with comprehensive API",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Kova AI System",
        "url": "https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting (100 requests per minute by default)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(ai_endpoints.router, tags=["AI Services"])
app.include_router(webhooks.router, tags=["Webhooks"])
app.include_router(database_endpoints.router, tags=["Database Operations"])

# Mount Prometheus metrics
app.mount("/metrics", make_asgi_app())


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponseModel(
            error=exc.detail if isinstance(exc.detail, str) else "HTTP Exception",
            detail=str(exc.detail) if not isinstance(exc.detail, str) else None,
            timestamp=datetime.utcnow(),
            path=str(request.url.path)
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with structured error response."""
    log_error(exc, f"Unhandled exception in {request.url.path}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponseModel(
            error="Internal server error",
            detail=str(exc) if settings.debug else "An unexpected error occurred",
            timestamp=datetime.utcnow(),
            path=str(request.url.path)
        ).dict()
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info(f"Starting {settings.app_name} v{settings.api_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")
    
    # Validate configuration
    if settings.validate_required_keys():
        logger.info("✅ All required API keys are configured")
    else:
        logger.warning("⚠️  Some API keys are missing - functionality may be limited")
    
    # Initialize database tables if needed
    try:
        from app.database.session import create_tables
        await create_tables()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database table initialization failed: {str(e)}")
    
    logger.info(f"🚀 {settings.app_name} startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to documentation."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.api_version,
        "docs": "/docs",
        "health": "/health",
        "status": "running",
        "features": [
            "AI-powered command processing",
            "GitHub webhook integration", 
            "Database operations",
            "Real-time monitoring",
            "Security & rate limiting"
        ],
        "timestamp": datetime.utcnow()
    }


@app.get("/info", tags=["System"])
async def system_info():
    """Get system information and capabilities."""
    return {
        "system": settings.app_name,
        "version": settings.api_version,
        "capabilities": {
            "ai_services": {
                "openai": bool(settings.openai_api_key),
                "anthropic": bool(settings.anthropic_api_key)
            },
            "integrations": {
                "github": bool(settings.github_token),
                "pinecone": bool(settings.pinecone_api_key)
            },
            "features": [
                "Health monitoring",
                "Database operations",
                "Webhook processing",
                "AI command processing",
                "Rate limiting",
                "Security headers",
                "Request logging",
                "Prometheus metrics"
            ]
        },
        "endpoints": {
            "health": "/health",
            "ai": "/ai/*",
            "webhooks": "/webhooks/*",
            "data": "/data/*",
            "docs": "/docs",
            "metrics": "/metrics"
        },
        "timestamp": datetime.utcnow()
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )
