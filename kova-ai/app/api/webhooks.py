"""
GitHub Webhooks API
Handles GitHub webhook events and forwards to Claude for processing
"""

from fastapi import APIRouter, Request, HTTPException, Header, BackgroundTasks
from typing import Optional
import hmac
import hashlib
import json
import os
import logging
from datetime import datetime

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")


def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify GitHub webhook signature"""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
        return True

    if not signature_header:
        return False

    hash_algorithm, github_signature = signature_header.split("=")
    algorithm = hashlib.sha256 if hash_algorithm == "sha256" else hashlib.sha1

    expected_signature = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        msg=payload_body,
        digestmod=algorithm
    ).hexdigest()

    return hmac.compare_digest(expected_signature, github_signature)


async def process_webhook_background(event_type: str, payload: dict, delivery_id: str):
    """Process webhook in background"""
    try:
        logger.info(f"Processing webhook: {event_type} - {delivery_id}")

        # TODO: Store in database
        # db_event = WebhookEvent(
        #     event_type=event_type,
        #     github_delivery_id=delivery_id,
        #     payload=payload
        # )

        # Process based on event type
        if event_type == "push":
            await handle_push_event(payload)
        elif event_type == "pull_request":
            await handle_pull_request_event(payload)
        elif event_type == "issues":
            await handle_issues_event(payload)
        elif event_type == "issue_comment":
            await handle_issue_comment_event(payload)
        elif event_type == "workflow_run":
            await handle_workflow_run_event(payload)
        else:
            logger.info(f"Unhandled event type: {event_type}")

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")


async def handle_push_event(payload: dict):
    """Handle push events"""
    repo_name = payload.get("repository", {}).get("full_name")
    ref = payload.get("ref")
    commits = payload.get("commits", [])

    logger.info(f"Push to {repo_name} on {ref}: {len(commits)} commits")

    # Forward to Claude for analysis
    analysis_data = {
        "event": "push",
        "repository": repo_name,
        "branch": ref,
        "commits": len(commits),
        "commit_messages": [c.get("message") for c in commits[:5]]
    }

    await forward_to_claude(analysis_data)


async def handle_pull_request_event(payload: dict):
    """Handle pull request events"""
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repo_name = payload.get("repository", {}).get("full_name")

    logger.info(f"PR {action} in {repo_name}: #{pr.get('number')} - {pr.get('title')}")

    analysis_data = {
        "event": "pull_request",
        "action": action,
        "repository": repo_name,
        "pr_number": pr.get("number"),
        "title": pr.get("title"),
        "body": pr.get("body"),
        "base_branch": pr.get("base", {}).get("ref"),
        "head_branch": pr.get("head", {}).get("ref")
    }

    await forward_to_claude(analysis_data)


async def handle_issues_event(payload: dict):
    """Handle issues events"""
    action = payload.get("action")
    issue = payload.get("issue", {})
    repo_name = payload.get("repository", {}).get("full_name")

    logger.info(f"Issue {action} in {repo_name}: #{issue.get('number')} - {issue.get('title')}")

    analysis_data = {
        "event": "issues",
        "action": action,
        "repository": repo_name,
        "issue_number": issue.get("number"),
        "title": issue.get("title"),
        "body": issue.get("body"),
        "labels": [label.get("name") for label in issue.get("labels", [])]
    }

    await forward_to_claude(analysis_data)


async def handle_issue_comment_event(payload: dict):
    """Handle issue comment events"""
    action = payload.get("action")
    comment = payload.get("comment", {})
    issue = payload.get("issue", {})
    repo_name = payload.get("repository", {}).get("full_name")

    logger.info(f"Comment {action} in {repo_name} on issue #{issue.get('number')}")

    analysis_data = {
        "event": "issue_comment",
        "action": action,
        "repository": repo_name,
        "issue_number": issue.get("number"),
        "comment_body": comment.get("body")
    }

    await forward_to_claude(analysis_data)


async def handle_workflow_run_event(payload: dict):
    """Handle workflow run events"""
    workflow_run = payload.get("workflow_run", {})
    repo_name = payload.get("repository", {}).get("full_name")
    status = workflow_run.get("status")
    conclusion = workflow_run.get("conclusion")

    logger.info(f"Workflow {status}/{conclusion} in {repo_name}")

    analysis_data = {
        "event": "workflow_run",
        "repository": repo_name,
        "workflow_name": workflow_run.get("name"),
        "status": status,
        "conclusion": conclusion,
        "run_number": workflow_run.get("run_number")
    }

    await forward_to_claude(analysis_data)


async def forward_to_claude(data: dict):
    """Forward webhook data to Claude for analysis"""
    import httpx

    claude_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not claude_api_key:
        logger.warning("ANTHROPIC_API_KEY not set, skipping Claude forwarding")
        return

    try:
        headers = {
            "Authorization": f"Bearer {claude_api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        prompt = f"""Analyze this GitHub webhook event:

{json.dumps(data, indent=2)}

Provide insights about:
1. What happened
2. Potential impact
3. Recommended actions
4. Any concerns or issues"""

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                analysis = result.get("content", [{}])[0].get("text", "")
                logger.info(f"Claude analysis: {analysis[:200]}...")
                return analysis
            else:
                logger.error(f"Claude API error: {response.status_code}")

    except Exception as e:
        logger.error(f"Error forwarding to Claude: {e}")


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: Optional[str] = Header(None),
    x_github_delivery: Optional[str] = Header(None),
    x_hub_signature_256: Optional[str] = Header(None)
):
    """
    GitHub webhook endpoint

    Receives and processes GitHub webhook events
    """
    try:
        # Get raw body for signature verification
        body = await request.body()

        # Verify signature
        if not verify_github_signature(body, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse payload
        payload = json.loads(body.decode())

        # Log event
        logger.info(f"Received GitHub webhook: {x_github_event} - {x_hub_signature_256}")

        # Process in background
        background_tasks.add_task(
            process_webhook_background,
            x_github_event,
            payload,
            x_hub_signature_256
        )

        return {
            "status": "accepted",
            "event": x_github_event,
            "delivery_id": x_hub_signature_256
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def webhook_status():
    """Get webhook configuration status"""
    return {
        "webhook_secret_configured": bool(GITHUB_WEBHOOK_SECRET),
        "claude_api_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "github_token_configured": bool(os.getenv("GITHUB_TOKEN")),
        "endpoint": "/webhooks/github",
        "supported_events": [
            "push",
            "pull_request",
            "issues",
            "issue_comment",
            "workflow_run"
        ]
    }
