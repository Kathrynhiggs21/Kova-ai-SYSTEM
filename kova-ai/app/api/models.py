from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Health Check Models
class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status of the service")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
    services: Dict[str, str] = Field(default_factory=dict, description="Status of dependent services")


# AI Command Models
class AICommandRequest(BaseModel):
    """Request model for AI command processing."""
    command: str = Field(..., min_length=1, max_length=10000, description="The command to process")
    context: Optional[str] = Field(default=None, description="Additional context for the command")
    model: str = Field(default="gpt-3.5-turbo", description="AI model to use")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens in response")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="Response creativity level")


class AICommandResponse(BaseModel):
    """Response model for AI command processing."""
    success: bool = Field(..., description="Whether the command was processed successfully")
    response: Optional[str] = Field(default=None, description="AI generated response")
    model_used: str = Field(..., description="AI model that processed the command")
    tokens_used: Optional[int] = Field(default=None, description="Number of tokens consumed")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    error: Optional[str] = Field(default=None, description="Error message if processing failed")


# GitHub Webhook Models
class GitHubRepository(BaseModel):
    """GitHub repository information."""
    id: int
    name: str
    full_name: str
    html_url: str
    clone_url: str
    default_branch: str


class GitHubCommit(BaseModel):
    """GitHub commit information."""
    id: str
    message: str
    timestamp: datetime
    author: Dict[str, str]
    url: str


class GitHubWebhookRequest(BaseModel):
    """Request model for GitHub webhook processing."""
    action: str = Field(..., description="The action that triggered the webhook")
    repository: GitHubRepository = Field(..., description="Repository information")
    commits: Optional[List[GitHubCommit]] = Field(default=None, description="Commits (for push events)")
    pull_request: Optional[Dict[str, Any]] = Field(default=None, description="Pull request data")
    issue: Optional[Dict[str, Any]] = Field(default=None, description="Issue data")


class GitHubWebhookResponse(BaseModel):
    """Response model for GitHub webhook processing."""
    success: bool = Field(..., description="Whether the webhook was processed successfully")
    action_taken: str = Field(..., description="Description of actions taken")
    processed_at: datetime = Field(default_factory=datetime.utcnow, description="When the webhook was processed")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional processing details")


# Database Models
class RepositoryCreate(BaseModel):
    """Model for creating a new repository record."""
    name: str = Field(..., min_length=1, max_length=255, description="Repository name")
    url: str = Field(..., description="Repository URL")


class RepositoryResponse(BaseModel):
    """Response model for repository data."""
    id: int
    name: str
    url: str

    class Config:
        from_attributes = True


class ErrorCreate(BaseModel):
    """Model for creating a new error record."""
    message: str = Field(..., min_length=1, description="Error message")


class ErrorResponse(BaseModel):
    """Response model for error data."""
    id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


# General API Models
class ErrorResponseModel(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the error occurred")
    path: Optional[str] = Field(default=None, description="API path where error occurred")


class SuccessResponse(BaseModel):
    """Standard success response model."""
    success: bool = Field(default=True, description="Indicates successful operation")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")