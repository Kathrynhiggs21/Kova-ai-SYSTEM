from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime

from app.api.models import (
    RepositoryCreate, RepositoryResponse, ErrorCreate, ErrorResponse,
    SuccessResponse, ErrorResponseModel
)
from app.database.operations import repository_ops, error_ops
from app.security.middleware import require_api_key, optional_api_key
from app.utils.logger import setup_logger, log_api_request, log_api_response

router = APIRouter(prefix="/data")
logger = setup_logger(__name__)


# Repository endpoints
@router.post("/repositories", response_model=RepositoryResponse, dependencies=[Depends(require_api_key)])
async def create_repository(repo_data: RepositoryCreate):
    """
    Create a new repository record.
    
    Requires authentication.
    """
    log_api_request("/data/repositories", "POST", {"name": repo_data.name})
    
    # Check if repository already exists
    existing = await repository_ops.get_repository_by_name(repo_data.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponseModel(
                error="Repository already exists",
                detail=f"A repository with name '{repo_data.name}' already exists",
                timestamp=datetime.utcnow(),
                path="/data/repositories"
            ).dict()
        )
    
    # Create new repository
    db_repo = await repository_ops.create_repository(repo_data)
    if not db_repo:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseModel(
                error="Failed to create repository",
                detail="Database operation failed",
                timestamp=datetime.utcnow(),
                path="/data/repositories"
            ).dict()
        )
    
    log_api_response("/data/repositories", 201, {"id": db_repo.id})
    return RepositoryResponse(id=db_repo.id, name=db_repo.name, url=db_repo.url)


@router.get("/repositories", response_model=List[RepositoryResponse])
async def list_repositories(
    authenticated: bool = Depends(optional_api_key),
    limit: int = Query(default=100, le=1000, description="Maximum number of repositories to return"),
    offset: int = Query(default=0, ge=0, description="Number of repositories to skip")
):
    """
    List repositories with pagination.
    
    Authentication optional - may return limited results for unauthenticated requests.
    """
    log_api_request("/data/repositories", "GET", {"limit": limit, "offset": offset, "authenticated": authenticated})
    
    # Limit results for unauthenticated users
    if not authenticated:
        limit = min(limit, 10)
    
    repositories = await repository_ops.list_repositories(limit=limit, offset=offset)
    
    log_api_response("/data/repositories", 200, {"count": len(repositories)})
    return [RepositoryResponse(id=repo.id, name=repo.name, url=repo.url) for repo in repositories]


@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: int,
    authenticated: bool = Depends(optional_api_key)
):
    """
    Get repository by ID.
    
    Authentication optional.
    """
    log_api_request(f"/data/repositories/{repo_id}", "GET", {"authenticated": authenticated})
    
    db_repo = await repository_ops.get_repository(repo_id)
    if not db_repo:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponseModel(
                error="Repository not found",
                detail=f"No repository with ID {repo_id}",
                timestamp=datetime.utcnow(),
                path=f"/data/repositories/{repo_id}"
            ).dict()
        )
    
    log_api_response(f"/data/repositories/{repo_id}", 200, {"name": db_repo.name})
    return RepositoryResponse(id=db_repo.id, name=db_repo.name, url=db_repo.url)


@router.put("/repositories/{repo_id}", response_model=RepositoryResponse, dependencies=[Depends(require_api_key)])
async def update_repository(repo_id: int, repo_data: RepositoryCreate):
    """
    Update repository.
    
    Requires authentication.
    """
    log_api_request(f"/data/repositories/{repo_id}", "PUT", {"name": repo_data.name})
    
    db_repo = await repository_ops.update_repository(repo_id, repo_data)
    if not db_repo:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponseModel(
                error="Repository not found",
                detail=f"No repository with ID {repo_id}",
                timestamp=datetime.utcnow(),
                path=f"/data/repositories/{repo_id}"
            ).dict()
        )
    
    log_api_response(f"/data/repositories/{repo_id}", 200, {"updated": True})
    return RepositoryResponse(id=db_repo.id, name=db_repo.name, url=db_repo.url)


@router.delete("/repositories/{repo_id}", response_model=SuccessResponse, dependencies=[Depends(require_api_key)])
async def delete_repository(repo_id: int):
    """
    Delete repository.
    
    Requires authentication.
    """
    log_api_request(f"/data/repositories/{repo_id}", "DELETE", {})
    
    deleted = await repository_ops.delete_repository(repo_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponseModel(
                error="Repository not found",
                detail=f"No repository with ID {repo_id}",
                timestamp=datetime.utcnow(),
                path=f"/data/repositories/{repo_id}"
            ).dict()
        )
    
    log_api_response(f"/data/repositories/{repo_id}", 200, {"deleted": True})
    return SuccessResponse(
        success=True,
        message=f"Repository {repo_id} deleted successfully",
        timestamp=datetime.utcnow()
    )


# Error endpoints
@router.post("/errors", response_model=ErrorResponse, dependencies=[Depends(require_api_key)])
async def create_error(error_data: ErrorCreate):
    """
    Create a new error record.
    
    Requires authentication.
    """
    log_api_request("/data/errors", "POST", {"message_length": len(error_data.message)})
    
    db_error = await error_ops.create_error(error_data)
    if not db_error:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponseModel(
                error="Failed to create error record",
                detail="Database operation failed",
                timestamp=datetime.utcnow(),
                path="/data/errors"
            ).dict()
        )
    
    log_api_response("/data/errors", 201, {"id": db_error.id})
    return ErrorResponse(id=db_error.id, message=db_error.message, created_at=db_error.created_at)


@router.get("/errors", response_model=List[ErrorResponse])
async def list_errors(
    authenticated: bool = Depends(optional_api_key),
    limit: int = Query(default=50, le=500, description="Maximum number of errors to return"),
    offset: int = Query(default=0, ge=0, description="Number of errors to skip")
):
    """
    List errors with pagination, newest first.
    
    Authentication optional - may return limited results for unauthenticated requests.
    """
    log_api_request("/data/errors", "GET", {"limit": limit, "offset": offset, "authenticated": authenticated})
    
    # Limit results for unauthenticated users
    if not authenticated:
        limit = min(limit, 5)
    
    errors = await error_ops.list_errors(limit=limit, offset=offset)
    
    log_api_response("/data/errors", 200, {"count": len(errors)})
    return [ErrorResponse(id=err.id, message=err.message, created_at=err.created_at) for err in errors]


@router.get("/errors/{error_id}", response_model=ErrorResponse, dependencies=[Depends(require_api_key)])
async def get_error(error_id: int):
    """
    Get error by ID.
    
    Requires authentication.
    """
    log_api_request(f"/data/errors/{error_id}", "GET", {})
    
    db_error = await error_ops.get_error(error_id)
    if not db_error:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponseModel(
                error="Error not found",
                detail=f"No error record with ID {error_id}",
                timestamp=datetime.utcnow(),
                path=f"/data/errors/{error_id}"
            ).dict()
        )
    
    log_api_response(f"/data/errors/{error_id}", 200, {"found": True})
    return ErrorResponse(id=db_error.id, message=db_error.message, created_at=db_error.created_at)


@router.delete("/errors/{error_id}", response_model=SuccessResponse, dependencies=[Depends(require_api_key)])
async def delete_error(error_id: int):
    """
    Delete error record.
    
    Requires authentication.
    """
    log_api_request(f"/data/errors/{error_id}", "DELETE", {})
    
    deleted = await error_ops.delete_error(error_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponseModel(
                error="Error not found",
                detail=f"No error record with ID {error_id}",
                timestamp=datetime.utcnow(),
                path=f"/data/errors/{error_id}"
            ).dict()
        )
    
    log_api_response(f"/data/errors/{error_id}", 200, {"deleted": True})
    return SuccessResponse(
        success=True,
        message=f"Error record {error_id} deleted successfully",
        timestamp=datetime.utcnow()
    )