from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import time
from datetime import datetime

from app.api.models import HealthResponse, ErrorResponseModel
from app.database.session import SessionLocal
from app.utils.logger import setup_logger, log_error
from app.core.config import settings

router = APIRouter()
logger = setup_logger(__name__)


@router.get("/health", response_model=HealthResponse, responses={503: {"model": ErrorResponseModel}})
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns the health status of the API and its dependencies including database connectivity.
    """
    start_time = time.time()
    services = {}
    
    try:
        # Check database connectivity
        try:
            async with SessionLocal() as session:
                result = await session.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()
                if row and row[0] == 1:
                    services["database"] = "healthy"
                    logger.info("Database health check passed")
                else:
                    services["database"] = "unhealthy"
                    logger.warning("Database health check returned unexpected result")
        except Exception as db_error:
            services["database"] = "unhealthy"
            logger.warning(f"Database health check failed: {str(db_error)}")
        
        # Check API key configuration
        api_keys_configured = settings.validate_required_keys()
        services["api_keys"] = "configured" if api_keys_configured else "missing"
        
        # Overall health status
        overall_healthy = all(status == "healthy" or status == "configured" for status in services.values())
        status = "ok" if overall_healthy else "degraded"
        
        processing_time = time.time() - start_time
        
        return HealthResponse(
            status=status,
            timestamp=datetime.utcnow(),
            version=settings.api_version,
            services={**services, "response_time_ms": f"{processing_time * 1000:.2f}"}
        )
        
    except Exception as e:
        log_error(e, "health_check")
        raise HTTPException(
            status_code=503,
            detail=ErrorResponseModel(
                error="Health check failed",
                detail=str(e),
                timestamp=datetime.utcnow(),
                path="/health"
            ).dict()
        )
