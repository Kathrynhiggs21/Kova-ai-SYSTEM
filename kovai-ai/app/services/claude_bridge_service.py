import os
import json
import logging
import asyncio
import httpx
from datetime import datetime, timedelta
from pathlib import Path

# Environment variable configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Updated to match standard env var

# Load Kova repos from config
def load_kova_repos():
    """Load Kova repositories from config file"""
    config_path = Path(__file__).parent.parent.parent.parent / "kova_repos_config.json"
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return [
                repo["full_name"]
                for repo in config.get("repositories", [])
                if repo.get("enabled", True)
            ]
    except Exception:
        # Fallback to default list
        return [
            'Kathrynhiggs21/Kova-ai-SYSTEM',
            'Kathrynhiggs21/kova-ai',
            'Kathrynhiggs21/kova-ai-site',
            'Kathrynhiggs21/kova-ai-mem0',
            'Kathrynhiggs21/kova-ai-docengine',
            'Kathrynhiggs21/Kova-AI-Scribbles'
        ]

KOVA_REPOS = load_kova_repos()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_repositories():
    while True:
        try:
            logger.info(f"Starting synchronization at {datetime.now()}")
            for repo in KOVA_REPOS:
                await sync_repo(repo)
            logger.info(f"Synchronization completed at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error during synchronization: {e}")
        await asyncio.sleep(300)  # Wait for 5 minutes

async def sync_repo(repo):
    """Sync a single repository with GitHub and Claude"""
    logger.info(f"Syncing repository: {repo}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch repo data from GitHub
            headers = {"Authorization": f"token {GITHUB_TOKEN}"}

            # Get basic repo info
            repo_response = await client.get(
                f"https://api.github.com/repos/{repo}",
                headers=headers
            )

            if repo_response.status_code == 404:
                logger.warning(f"Repository {repo} not found - may need to be created")
                return {"status": "not_found", "repo": repo}

            repo_data = repo_response.json()

            # Get recent commits
            commits_response = await client.get(
                f"https://api.github.com/repos/{repo}/commits?per_page=5",
                headers=headers
            )
            commits = commits_response.json() if commits_response.status_code == 200 else []

            sync_data = {
                "repo": repo,
                "name": repo_data.get("name"),
                "updated_at": repo_data.get("updated_at"),
                "recent_commits": len(commits),
                "default_branch": repo_data.get("default_branch"),
                "status": "synced"
            }

            # Send to Claude for analysis
            if CLAUDE_API_KEY:
                await communicate_with_claude_api(sync_data)

            logger.info(f"Successfully synced {repo}")
            return sync_data

    except Exception as e:
        logger.error(f"Error syncing {repo}: {e}")
        return {"status": "error", "repo": repo, "error": str(e)}

async def manual_sync():
    for repo in KOVA_REPOS:
        await sync_repo(repo)

async def communicate_with_claude_api(data):
    """Communicate with Claude API using correct Anthropic endpoint"""
    if not CLAUDE_API_KEY:
        logger.warning("Claude API key not configured - skipping Claude sync")
        return {"status": "skipped", "reason": "no_api_key"}

    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": f"Analyze this Kova AI repository sync data:\n\n{json.dumps(data, indent=2)}\n\nProvide a brief summary of the repository status."
        }]
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "analysis": result.get("content", [{}])[0].get("text", "No response")
                }
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error": f"API returned {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Failed to communicate with Claude API: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(sync_repositories())
    except KeyboardInterrupt:
        logger.info("Manual sync initiated")
        loop.run_until_complete(manual_sync())
    finally:
        loop.close()