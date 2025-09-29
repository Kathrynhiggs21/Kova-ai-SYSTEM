from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
import uvicorn
from datetime import datetime

from app.api import health, ai_endpoints, webhooks
from app.core.config import settings
from app.utils.logger import setup_logger, log_error
from app.api.models import ErrorResponseModel

# Setup logging
logger = setup_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.api_version,
    description="Kova AI System - AI-powered development automation platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
