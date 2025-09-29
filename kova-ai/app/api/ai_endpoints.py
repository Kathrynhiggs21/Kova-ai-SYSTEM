from fastapi import APIRouter, HTTPException, Depends
import time
from datetime import datetime

from app.api.models import AICommandRequest, AICommandResponse, ErrorResponseModel
from app.integrations.openai_client import openai_client
from app.utils.logger import setup_logger, log_api_request, log_api_response, log_error
from app.core.config import settings

router = APIRouter(prefix="/ai")
logger = setup_logger(__name__)


@router.post("/command", response_model=AICommandResponse, responses={400: {"model": ErrorResponseModel}, 503: {"model": ErrorResponseModel}})
async def process_ai_command(request: AICommandRequest):
    """
    Process an AI command using configured AI services.
    
    This endpoint accepts a command and processes it using OpenAI's API.
    Requires OPENAI_API_KEY to be configured in environment variables.
    """
    start_time = time.time()
    
    try:
        log_api_request("/ai/command", "POST", {
            "command_length": len(request.command),
            "model": request.model,
            "has_context": bool(request.context)
        })
        
        # Check if OpenAI is configured
        if not openai_client.is_configured():
            raise HTTPException(
                status_code=503,
                detail=ErrorResponseModel(
                    error="AI service not configured",
                    detail="OpenAI API key is required but not configured. Please set OPENAI_API_KEY in environment.",
                    timestamp=datetime.utcnow(),
                    path="/ai/command"
                ).dict()
            )
        
        # Process the command using OpenAI
        result = await openai_client.chat_completion(
            messages=[
                {
                    "role": "system", 
                    "content": "You are Kova AI, a helpful assistant for development automation and system management. Provide clear, actionable responses."
                },
                {
                    "role": "system",
                    "content": f"Additional context: {request.context}" if request.context else "No additional context provided."
                },
                {
                    "role": "user",
                    "content": request.command
                }
            ],
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        processing_time = time.time() - start_time
        
        if result.get("success"):
            response = AICommandResponse(
                success=True,
                response=result.get("response"),
                model_used=result.get("model_used", request.model),
                tokens_used=result.get("tokens_used"),
                processing_time=processing_time,
                error=None
            )
            
            log_api_response("/ai/command", 200, {
                "success": True,
                "tokens_used": result.get("tokens_used"),
                "processing_time": processing_time
            })
            
            return response
        else:
            # OpenAI returned an error
            error_detail = result.get("error", "Unknown error occurred")
            
            response = AICommandResponse(
                success=False,
                response=None,
                model_used=request.model,
                tokens_used=None,
                processing_time=processing_time,
                error=error_detail
            )
            
            log_api_response("/ai/command", 200, {
                "success": False,
                "error": error_detail,
                "processing_time": processing_time
            })
            
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        log_error(e, "process_ai_command")
        
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseModel(
                error="Internal server error",
                detail=str(e),
                timestamp=datetime.utcnow(),
                path="/ai/command"
            ).dict()
        )


@router.get("/status")
async def ai_service_status():
    """
    Get the status of AI service integrations.
    
    Returns information about which AI services are configured and available.
    """
    try:
        services = {
            "openai": {
                "configured": openai_client.is_configured(),
                "service": "OpenAI GPT Models"
            },
            "anthropic": {
                "configured": bool(settings.anthropic_api_key),
                "service": "Anthropic Claude (Not yet integrated)"
            }
        }
        
        overall_status = "ready" if any(s["configured"] for s in services.values()) else "not_configured"
        
        return {
            "status": overall_status,
            "services": services,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        log_error(e, "ai_service_status")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseModel(
                error="Failed to get AI service status",
                detail=str(e),
                timestamp=datetime.utcnow(),
                path="/ai/status"
            ).dict()
        )
