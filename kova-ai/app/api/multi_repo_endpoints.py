"""
Multi-Repository Management API Endpoints

Provides endpoints for managing and syncing multiple Kova AI repositories.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.services.multi_repo_sync_service import MultiRepoSyncService

router = APIRouter(prefix="/multi-repo", tags=["multi-repo"])


class RepoAddRequest(BaseModel):
    repo_full_name: str
    repo_type: Optional[str] = "service"
    description: Optional[str] = None


class RepoSyncRequest(BaseModel):
    repos: Optional[List[str]] = None  # If None, sync all
    include_claude: bool = False


class RepoStatusResponse(BaseModel):
    status: str
    data: Dict[str, Any]


@router.get("/status", response_model=RepoStatusResponse)
async def get_multi_repo_status():
    """Get status of all Kova AI repositories"""
    try:
        service = MultiRepoSyncService()
        status = await service.get_cross_repo_status()

        return RepoStatusResponse(
            status="success",
            data=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=RepoStatusResponse)
async def sync_repositories(request: RepoSyncRequest):
    """Sync all or specific Kova AI repositories"""
    try:
        service = MultiRepoSyncService()

        # Sync repositories
        sync_results = await service.sync_all_repositories()

        # Optionally sync with Claude
        claude_results = {}
        if request.include_claude:
            for repo, result in sync_results.items():
                if result.get("status") == "success" and result.get("data", {}).get("exists"):
                    claude_results[repo] = await service.sync_with_claude(result["data"])

        return RepoStatusResponse(
            status="success",
            data={
                "sync_results": sync_results,
                "claude_results": claude_results if request.include_claude else {},
                "repos_synced": len(sync_results)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discover", response_model=RepoStatusResponse)
async def discover_new_repos():
    """Discover new Kova AI repositories"""
    try:
        service = MultiRepoSyncService()
        new_repos = await service.discover_new_repos()

        return RepoStatusResponse(
            status="success",
            data={
                "new_repos": new_repos,
                "count": len(new_repos)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add", response_model=RepoStatusResponse)
async def add_repository(request: RepoAddRequest):
    """Add a new repository to the Kova AI system"""
    try:
        service = MultiRepoSyncService()
        success = await service.add_repo_to_config(
            request.repo_full_name,
            request.repo_type
        )

        if success:
            return RepoStatusResponse(
                status="success",
                data={
                    "message": f"Repository {request.repo_full_name} added successfully",
                    "repo": request.repo_full_name
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to add repository")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=RepoStatusResponse)
async def list_repositories():
    """List all configured Kova AI repositories"""
    try:
        service = MultiRepoSyncService()
        repos = service.get_enabled_repos()

        return RepoStatusResponse(
            status="success",
            data={
                "repositories": repos,
                "count": len(repos)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=RepoStatusResponse)
async def get_repo_config():
    """Get the full repository configuration"""
    try:
        service = MultiRepoSyncService()

        return RepoStatusResponse(
            status="success",
            data=service.config
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
