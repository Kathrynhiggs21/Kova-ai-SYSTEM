import logging
import sys
from typing import Any, Dict

from app.core.config import settings


def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup structured logger for the application."""
    
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    # Set log level from settings
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


def log_api_request(endpoint: str, method: str, data: Dict[str, Any] = None) -> None:
    """Log API request details."""
    logger = setup_logger("api.request")
    logger.info(f"{method} {endpoint}", extra={"data": data})


def log_api_response(endpoint: str, status_code: int, response_data: Dict[str, Any] = None) -> None:
    """Log API response details."""
    logger = setup_logger("api.response")
    logger.info(f"{endpoint} - Status: {status_code}", extra={"response": response_data})


def log_error(error: Exception, context: str = "") -> None:
    """Log error with context."""
    logger = setup_logger("error")
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def log_ai_integration(service: str, action: str, success: bool, details: Dict[str, Any] = None) -> None:
    """Log AI service integration calls."""
    logger = setup_logger("ai.integration")
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"AI Integration - {service}.{action}: {status}", extra={"details": details})