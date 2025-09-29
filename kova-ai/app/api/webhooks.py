from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional
import hashlib
import hmac
import json
from datetime import datetime

from app.api.models import GitHubWebhookResponse, ErrorResponseModel
from app.utils.logger import setup_logger, log_api_request, log_api_response, log_error
from app.core.config import settings

router = APIRouter(prefix="/webhooks")
logger = setup_logger(__name__)


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not secret or not signature:
        return False
        
    expected_signature = "sha256=" + hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@router.post("/github", response_model=GitHubWebhookResponse, responses={400: {"model": ErrorResponseModel}, 401: {"model": ErrorResponseModel}})
async def github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events.
    
    Processes various GitHub events like push, pull_request, issues, etc.
    Supports signature verification if GitHub webhook secret is configured.
    """
    try:
        # Get raw payload
        payload = await request.body()
        
        log_api_request("/webhooks/github", "POST", {
            "event_type": x_github_event,
            "payload_size": len(payload),
            "has_signature": bool(x_hub_signature_256)
        })
        
        # Verify signature if GitHub token is configured (used as webhook secret)
        if settings.github_token and x_hub_signature_256:
            if not verify_github_signature(payload, x_hub_signature_256, settings.github_token):
                raise HTTPException(
                    status_code=401,
                    detail=ErrorResponseModel(
                        error="Invalid signature",
                        detail="GitHub webhook signature verification failed",
                        timestamp=datetime.utcnow(),
                        path="/webhooks/github"
                    ).dict()
                )
        
        # Parse JSON payload
        try:
            data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=ErrorResponseModel(
                    error="Invalid JSON payload",
                    detail=str(e),
                    timestamp=datetime.utcnow(),
                    path="/webhooks/github"
                ).dict()
            )
        
        # Process different event types
        action_taken = await process_github_event(x_github_event, data)
        
        response = GitHubWebhookResponse(
            success=True,
            action_taken=action_taken,
            processed_at=datetime.utcnow(),
            details={
                "event_type": x_github_event,
                "repository": data.get("repository", {}).get("full_name", "unknown"),
                "action": data.get("action", "unknown")
            }
        )
        
        log_api_response("/webhooks/github", 200, {
            "success": True,
            "event_type": x_github_event,
            "action_taken": action_taken
        })
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, "github_webhook")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseModel(
                error="Webhook processing failed",
                detail=str(e),
                timestamp=datetime.utcnow(),
                path="/webhooks/github"
            ).dict()
        )


async def process_github_event(event_type: str, data: dict) -> str:
    """
    Process different types of GitHub events.
    
    Args:
        event_type: The type of GitHub event (push, pull_request, issues, etc.)
        data: The webhook payload data
        
    Returns:
        Description of the action taken
    """
    if not event_type:
        return "Received webhook without event type - logged for analysis"
    
    repository = data.get("repository", {})
    repo_name = repository.get("full_name", "unknown")
    
    if event_type == "push":
        commits = data.get("commits", [])
        branch = data.get("ref", "unknown").replace("refs/heads/", "")
        
        logger.info(f"Push event received: {len(commits)} commits to {repo_name}:{branch}")
        
        # Here you could add logic to:
        # - Trigger CI/CD pipelines
        # - Analyze code changes
        # - Send notifications
        
        return f"Processed push event: {len(commits)} commits to {branch}"
        
    elif event_type == "pull_request":
        action = data.get("action", "unknown")
        pr_number = data.get("pull_request", {}).get("number", "unknown")
        
        logger.info(f"Pull request {action}: #{pr_number} in {repo_name}")
        
        # Here you could add logic to:
        # - Review code changes
        # - Run automated tests
        # - Add comments or labels
        
        return f"Processed pull request {action}: #{pr_number}"
        
    elif event_type == "issues":
        action = data.get("action", "unknown")
        issue_number = data.get("issue", {}).get("number", "unknown")
        
        logger.info(f"Issue {action}: #{issue_number} in {repo_name}")
        
        # Here you could add logic to:
        # - Categorize issues
        # - Auto-assign based on content
        # - Send notifications
        
        return f"Processed issue {action}: #{issue_number}"
        
    elif event_type == "release":
        action = data.get("action", "unknown")
        release_tag = data.get("release", {}).get("tag_name", "unknown")
        
        logger.info(f"Release {action}: {release_tag} in {repo_name}")
        
        return f"Processed release {action}: {release_tag}"
        
    else:
        logger.info(f"Received unsupported event type: {event_type} from {repo_name}")
        return f"Logged unsupported event type: {event_type}"


@router.get("/github/status")
async def github_webhook_status():
    """Get the status of GitHub webhook integration."""
    return {
        "configured": bool(settings.github_token),
        "supports_signature_verification": bool(settings.github_token),
        "supported_events": [
            "push",
            "pull_request", 
            "issues",
            "release"
        ],
        "timestamp": datetime.utcnow()
    }
