"""
Multi-Repository Sync Service for Kova AI System

This service manages synchronization across all Kova AI repositories,
enabling cross-repo coordination, updates, and Claude AI integration.
"""

import os
import json
import logging
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiRepoSyncService:
    """Manages synchronization across all Kova AI repositories"""

    def __init__(self, github_token: str = None, claude_api_key: str = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.claude_api_key = claude_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.config = self._load_config()
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load multi-repo configuration"""
        config_path = Path(__file__).parent.parent.parent.parent / "kova_repos_config.json"

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file not found"""
        return {
            "github_owner": "Kathrynhiggs21",
            "repositories": [
                {"full_name": "Kathrynhiggs21/Kova-ai-SYSTEM", "enabled": True},
                {"full_name": "Kathrynhiggs21/kova-ai", "enabled": True},
                {"full_name": "Kathrynhiggs21/kova-ai-site", "enabled": True},
                {"full_name": "Kathrynhiggs21/kova-ai-mem0", "enabled": True},
                {"full_name": "Kathrynhiggs21/kova-ai-docengine", "enabled": True},
                {"full_name": "Kathrynhiggs21/Kova-AI-Scribbles", "enabled": True}
            ]
        }

    def get_enabled_repos(self) -> List[str]:
        """Get list of enabled repositories"""
        return [
            repo["full_name"]
            for repo in self.config.get("repositories", [])
            if repo.get("enabled", True)
        ]

    async def sync_all_repositories(self) -> Dict[str, Any]:
        """Sync all enabled repositories"""
        logger.info("Starting multi-repo sync...")

        repos = self.get_enabled_repos()
        results = {}

        async with httpx.AsyncClient(timeout=30.0) as client:
            for repo_full_name in repos:
                try:
                    logger.info(f"Syncing {repo_full_name}...")
                    repo_data = await self._sync_single_repo(client, repo_full_name)
                    results[repo_full_name] = {
                        "status": "success",
                        "data": repo_data,
                        "synced_at": datetime.now().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Failed to sync {repo_full_name}: {e}")
                    results[repo_full_name] = {
                        "status": "error",
                        "error": str(e),
                        "synced_at": datetime.now().isoformat()
                    }

        logger.info("Multi-repo sync completed")
        return results

    async def _sync_single_repo(self, client: httpx.AsyncClient, repo_full_name: str) -> Dict[str, Any]:
        """Sync a single repository"""
        # Get repo info
        repo_response = await client.get(
            f"{self.base_url}/repos/{repo_full_name}",
            headers=self.headers
        )

        if repo_response.status_code == 404:
            return {
                "exists": False,
                "message": f"Repository {repo_full_name} not found - may need to be created"
            }

        repo_response.raise_for_status()
        repo_data = repo_response.json()

        # Get recent commits
        commits_response = await client.get(
            f"{self.base_url}/repos/{repo_full_name}/commits?per_page=5",
            headers=self.headers
        )
        commits = commits_response.json() if commits_response.status_code == 200 else []

        # Get branches
        branches_response = await client.get(
            f"{self.base_url}/repos/{repo_full_name}/branches",
            headers=self.headers
        )
        branches = branches_response.json() if branches_response.status_code == 200 else []

        return {
            "exists": True,
            "name": repo_data.get("name"),
            "full_name": repo_data.get("full_name"),
            "description": repo_data.get("description"),
            "default_branch": repo_data.get("default_branch"),
            "updated_at": repo_data.get("updated_at"),
            "branches": [b["name"] for b in branches],
            "recent_commits": len(commits),
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0)
        }

    async def discover_new_repos(self) -> List[str]:
        """Auto-discover new Kova AI repositories"""
        logger.info("Discovering new Kova AI repositories...")

        owner = self.config.get("github_owner", "Kathrynhiggs21")
        pattern = self.config.get("discovery_settings", {}).get("repo_name_pattern", "kova")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/users/{owner}/repos?per_page=100",
                headers=self.headers
            )

            if response.status_code != 200:
                logger.error(f"Failed to fetch repos: {response.status_code}")
                return []

            all_repos = response.json()

            # Filter for Kova-related repos
            kova_repos = [
                repo["full_name"]
                for repo in all_repos
                if pattern.lower() in repo["name"].lower()
            ]

            # Find new repos not in config
            known_repos = set(self.get_enabled_repos())
            new_repos = [repo for repo in kova_repos if repo not in known_repos]

            if new_repos:
                logger.info(f"Discovered {len(new_repos)} new repos: {new_repos}")
            else:
                logger.info("No new repos discovered")

            return new_repos

    async def add_repo_to_config(self, repo_full_name: str, repo_type: str = "service") -> bool:
        """Add a new repository to the configuration"""
        config_path = Path(__file__).parent.parent.parent.parent / "kova_repos_config.json"

        try:
            # Check if repo exists on GitHub
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo_full_name}",
                    headers=self.headers
                )

                if response.status_code == 404:
                    logger.warning(f"Repository {repo_full_name} not found on GitHub")
                    # Still add it as planned
                    repo_info = {
                        "name": repo_full_name.split("/")[-1],
                        "description": "Planned repository"
                    }
                else:
                    repo_info = response.json()

            # Load current config
            with open(config_path, 'r') as f:
                config = json.load(f)

            # Check if already exists
            existing = [r for r in config["repositories"] if r["full_name"] == repo_full_name]
            if existing:
                logger.info(f"Repository {repo_full_name} already in config")
                return True

            # Add new repo
            new_repo = {
                "name": repo_info.get("name", repo_full_name.split("/")[-1]),
                "full_name": repo_full_name,
                "description": repo_info.get("description", "Kova AI repository"),
                "type": repo_type,
                "enabled": True,
                "sync_priority": 3,
                "features": []
            }

            config["repositories"].append(new_repo)

            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Added {repo_full_name} to config")
            return True

        except Exception as e:
            logger.error(f"Failed to add repo to config: {e}")
            return False

    async def sync_with_claude(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send repository data to Claude API for analysis"""
        if not self.claude_api_key:
            return {"error": "Claude API key not configured"}

        headers = {
            "Authorization": f"Bearer {self.claude_api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4000,
            "messages": [{
                "role": "user",
                "content": f"Analyze this Kova AI repository data:\n\n{json.dumps(repo_data, indent=2)}"
            }]
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
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
                    return {
                        "status": "error",
                        "error": f"Claude API returned {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"Failed to sync with Claude: {e}")
            return {"status": "error", "error": str(e)}

    async def get_cross_repo_status(self) -> Dict[str, Any]:
        """Get status of all repositories"""
        repos = self.get_enabled_repos()

        status = {
            "total_repos": len(repos),
            "repos": {},
            "timestamp": datetime.now().isoformat()
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for repo_full_name in repos:
                try:
                    response = await client.get(
                        f"{self.base_url}/repos/{repo_full_name}",
                        headers=self.headers
                    )

                    if response.status_code == 200:
                        repo_data = response.json()
                        status["repos"][repo_full_name] = {
                            "exists": True,
                            "updated_at": repo_data.get("updated_at"),
                            "default_branch": repo_data.get("default_branch"),
                            "open_issues": repo_data.get("open_issues_count", 0)
                        }
                    else:
                        status["repos"][repo_full_name] = {
                            "exists": False,
                            "status": "not_found_or_planned"
                        }
                except Exception as e:
                    status["repos"][repo_full_name] = {
                        "exists": False,
                        "error": str(e)
                    }

        return status


async def main():
    """Main entry point for testing"""
    service = MultiRepoSyncService()

    # Discover new repos
    new_repos = await service.discover_new_repos()
    if new_repos:
        print(f"\nDiscovered new repos: {new_repos}")

    # Sync all repos
    print("\nSyncing all repositories...")
    results = await service.sync_all_repositories()

    for repo, result in results.items():
        status = result.get("status")
        print(f"\n{repo}: {status}")
        if status == "success":
            data = result.get("data", {})
            if data.get("exists"):
                print(f"  - Branches: {data.get('branches', [])}")
                print(f"  - Recent commits: {data.get('recent_commits', 0)}")
            else:
                print(f"  - {data.get('message', 'Repository needs to be created')}")


if __name__ == "__main__":
    asyncio.run(main())
