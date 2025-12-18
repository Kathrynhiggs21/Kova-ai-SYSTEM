# Kova AI System - Code-Level Integration Reference

This document provides detailed code-level documentation for all integrations and connections in the Kova AI System.

---

## Table of Contents

1. [Claude AI Integration Code](#claude-ai-integration-code)
2. [GitHub Integration Code](#github-integration-code)
3. [Database Integration Code](#database-integration-code)
4. [Multi-Repository Sync Code](#multi-repository-sync-code)
5. [Webhook Processing Code](#webhook-processing-code)
6. [Artifact Generation Code](#artifact-generation-code)
7. [Service Initialization Code](#service-initialization-code)

---

## Claude AI Integration Code

### File: `kova-ai/app/services/claude_connector.py`

#### ClaudeConnector Class Structure

```python
from enum import Enum
from typing import Optional, Dict, Any, List
import httpx

class ArtifactType(str, Enum):
    """Supported artifact types for Claude generation"""
    CODE = "code"
    DOCUMENT = "document"
    DIAGRAM = "diagram"
    CONFIG = "config"
    DATA = "data"

class ClaudeConnector:
    """
    Main connector for Anthropic's Claude AI API.
    Handles all AI-related operations including:
    - Message sending with conversation context
    - Code generation and analysis
    - Document and diagram generation
    - Configuration file generation
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-3-sonnet-20240229"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
```

#### Message Sending Implementation

```python
async def send_message(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    conversation_history: Optional[List[Dict]] = None,
    max_tokens: int = 4096
) -> Dict[str, Any]:
    """
    Send a message to Claude and receive a response.

    Args:
        prompt: The user's message/prompt
        system_prompt: Optional system context
        conversation_history: Previous messages for context
        max_tokens: Maximum response length

    Returns:
        Dict containing response text and metadata
    """
    messages = []

    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)

    # Add current prompt
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": self.MODEL,
        "max_tokens": max_tokens,
        "messages": messages
    }

    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient() as client:
        response = await client.post(
            self.API_URL,
            headers=self.headers,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()
```

#### Code Generation Implementation

```python
async def generate_code(
    self,
    description: str,
    language: str = "python",
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate code based on description.

    Args:
        description: What the code should do
        language: Target programming language
        context: Additional context (existing code, requirements)

    Returns:
        Generated code with explanation
    """
    system_prompt = f"""You are an expert {language} developer.
Generate clean, well-documented, production-ready code.
Follow best practices and include error handling."""

    prompt = f"Generate {language} code for: {description}"
    if context:
        prompt += f"\n\nContext:\n{context}"

    return await self.send_message(prompt, system_prompt)
```

#### Code Analysis Implementation

```python
async def analyze_code(
    self,
    code: str,
    analysis_type: str = "full"
) -> Dict[str, Any]:
    """
    Analyze code for bugs, security issues, and improvements.

    Args:
        code: Source code to analyze
        analysis_type: Type of analysis (full, security, performance, bugs)

    Returns:
        Analysis results with recommendations
    """
    analysis_prompts = {
        "full": "Perform comprehensive code review",
        "security": "Identify security vulnerabilities",
        "performance": "Find performance bottlenecks",
        "bugs": "Detect potential bugs and issues"
    }

    system_prompt = """You are a senior code reviewer.
Provide detailed, actionable feedback with specific line references.
Categorize issues by severity: critical, high, medium, low."""

    prompt = f"""{analysis_prompts.get(analysis_type, analysis_prompts['full'])}:

```
{code}
```"""

    return await self.send_message(prompt, system_prompt)
```

---

## GitHub Integration Code

### File: `kova-ai/app/api/webhooks.py`

#### Webhook Handler Implementation

```python
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from typing import Dict, Any
import os

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_github_signature(payload: bytes, signature: str) -> bool:
    """
    Verify GitHub webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not GITHUB_WEBHOOK_SECRET:
        return False

    expected_signature = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        f"sha256={expected_signature}",
        signature
    )

@router.post("/github")
async def handle_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Handle incoming GitHub webhook events.

    Supported events:
    - push: Code pushed to repository
    - pull_request: PR opened/closed/merged
    - issues: Issue created/updated
    - issue_comment: Comment on issue
    - workflow_run: CI/CD workflow completed
    """
    # Get raw body for signature verification
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Verify signature
    if not verify_github_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse event
    event_type = request.headers.get("X-GitHub-Event", "")
    payload = await request.json()

    # Queue background processing
    background_tasks.add_task(
        process_webhook_background,
        event_type,
        payload
    )

    return {"status": "accepted", "event": event_type}
```

#### Background Webhook Processing

```python
async def process_webhook_background(
    event_type: str,
    payload: Dict[str, Any]
) -> None:
    """
    Process webhook event in background.

    Args:
        event_type: GitHub event type
        payload: Event payload data
    """
    handlers = {
        "push": handle_push_event,
        "pull_request": handle_pull_request_event,
        "issues": handle_issue_event,
        "issue_comment": handle_comment_event,
        "workflow_run": handle_workflow_event
    }

    handler = handlers.get(event_type)
    if handler:
        await handler(payload)
        await forward_to_claude(event_type, payload)

async def forward_to_claude(
    event_type: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Forward webhook event to Claude for analysis.

    Args:
        event_type: Type of GitHub event
        payload: Event data

    Returns:
        Claude's analysis of the event
    """
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Analyze this GitHub {event_type} event:
Repository: {payload.get('repository', {}).get('full_name')}
Action: {payload.get('action', 'N/A')}

Provide insights and recommended actions."""

    return await connector.send_message(
        prompt,
        system_prompt="You are a GitHub event analyzer."
    )
```

### File: `kova-ai/app/api/ai_endpoints.py`

#### GitHub API Integration

```python
import httpx
from typing import Dict, Any, List
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_BASE = "https://api.github.com"

async def fetch_repository_data(
    owner: str,
    repo: str
) -> Dict[str, Any]:
    """
    Fetch comprehensive repository data from GitHub.

    Args:
        owner: Repository owner/organization
        repo: Repository name

    Returns:
        Repository metadata, files, and recent activity
    """
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        # Fetch repository info
        repo_response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}",
            headers=headers
        )
        repo_data = repo_response.json()

        # Fetch recent commits
        commits_response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/commits",
            headers=headers,
            params={"per_page": 10}
        )
        commits = commits_response.json()

        # Fetch file tree
        default_branch = repo_data.get("default_branch", "main")
        tree_response = await client.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/git/trees/{default_branch}",
            headers=headers,
            params={"recursive": "1"}
        )
        tree = tree_response.json()

        return {
            "repository": repo_data,
            "recent_commits": commits,
            "file_tree": tree.get("tree", [])
        }
```

---

## Database Integration Code

### File: `kova-ai/app/database/session.py`

#### Async Database Session Configuration

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
import os

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://kova:kova_pass@db:5432/kova"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """
    Dependency for FastAPI routes to get database session.

    Yields:
        AsyncSession: Database session

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### File: `kova-ai/app/database/models.py`

#### SQLAlchemy ORM Models

```python
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, JSON, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base
import enum

class SeverityLevel(str, enum.Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Repository(Base):
    """Repository tracking model"""
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    full_name = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=5)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    errors = relationship("Error", back_populates="repository")
    sync_logs = relationship("SyncLog", back_populates="repository")

class Error(Base):
    """Error tracking model"""
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    error_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MEDIUM)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    repository = relationship("Repository", back_populates="errors")

class SyncLog(Base):
    """Synchronization history model"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    sync_type = Column(String(50), nullable=False)  # full, incremental, manual
    status = Column(String(50), nullable=False)  # started, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    details = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="sync_logs")

class WebhookEvent(Base):
    """GitHub webhook event storage"""
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ClaudeInteraction(Base):
    """Claude AI interaction logging"""
    __tablename__ = "claude_interactions"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    model = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Artifact(Base):
    """AI-generated artifact storage"""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    artifact_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Multi-Repository Sync Code

### File: `kova-ai/app/services/multi_repo_sync_service.py`

#### MultiRepoSyncService Implementation

```python
import asyncio
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import httpx
from datetime import datetime

class MultiRepoSyncService:
    """
    Service for synchronizing multiple Kova AI repositories.
    Handles discovery, sync operations, and status tracking.
    """

    CONFIG_PATH = Path("/home/user/Kova-ai-SYSTEM/kova_repos_config.json")
    GITHUB_API = "https://api.github.com"

    def __init__(self, github_token: str, anthropic_api_key: str):
        self.github_token = github_token
        self.anthropic_api_key = anthropic_api_key
        self.config = self._load_config()
        self._sync_status: Dict[str, Any] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load multi-repo configuration from JSON file."""
        try:
            with open(self.CONFIG_PATH) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"repositories": [], "github_owner": ""}

    @property
    def github_owner(self) -> str:
        """Get configured GitHub owner."""
        return self.config.get("github_owner", "Kathrynhiggs21")

    @property
    def repositories(self) -> List[Dict[str, Any]]:
        """Get configured repositories list."""
        return self.config.get("repositories", [])

    async def sync_all_repos(
        self,
        use_claude: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronize all configured repositories.

        Args:
            use_claude: Whether to use Claude for analysis

        Returns:
            Sync results for all repositories
        """
        results = {}

        # Sort by priority
        sorted_repos = sorted(
            self.repositories,
            key=lambda r: r.get("priority", 5)
        )

        for repo in sorted_repos:
            repo_name = repo["name"]
            try:
                result = await self.sync_repository(
                    repo_name,
                    use_claude=use_claude
                )
                results[repo_name] = {
                    "status": "success",
                    "data": result
                }
            except Exception as e:
                results[repo_name] = {
                    "status": "error",
                    "error": str(e)
                }

        return results

    async def sync_repository(
        self,
        repo_name: str,
        use_claude: bool = True
    ) -> Dict[str, Any]:
        """
        Sync a single repository with retry logic.

        Args:
            repo_name: Name of repository to sync
            use_claude: Whether to analyze with Claude

        Returns:
            Repository sync data
        """
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                # Fetch repository data
                repo_data = await self._fetch_repo_data(repo_name)

                # Analyze with Claude if requested
                if use_claude:
                    analysis = await self._analyze_with_claude(
                        repo_name,
                        repo_data
                    )
                    repo_data["claude_analysis"] = analysis

                # Update sync status
                self._sync_status[repo_name] = {
                    "last_sync": datetime.utcnow().isoformat(),
                    "status": "synced"
                }

                return repo_data

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise

        raise Exception(f"Failed to sync {repo_name} after {max_retries} retries")

    async def _fetch_repo_data(
        self,
        repo_name: str
    ) -> Dict[str, Any]:
        """Fetch repository data from GitHub API."""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        async with httpx.AsyncClient() as client:
            # Get repo info
            repo_url = f"{self.GITHUB_API}/repos/{self.github_owner}/{repo_name}"
            response = await client.get(repo_url, headers=headers)
            response.raise_for_status()
            repo_info = response.json()

            # Get recent commits
            commits_url = f"{repo_url}/commits"
            commits_response = await client.get(
                commits_url,
                headers=headers,
                params={"per_page": 5}
            )
            commits = commits_response.json()

            return {
                "info": repo_info,
                "recent_commits": commits,
                "fetched_at": datetime.utcnow().isoformat()
            }

    async def _analyze_with_claude(
        self,
        repo_name: str,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze repository with Claude AI."""
        from .claude_connector import ClaudeConnector

        connector = ClaudeConnector(self.anthropic_api_key)

        prompt = f"""Analyze this repository and provide insights:
Repository: {repo_name}
Description: {repo_data['info'].get('description', 'N/A')}
Language: {repo_data['info'].get('language', 'N/A')}
Recent activity: {len(repo_data['recent_commits'])} commits

Provide:
1. Repository health assessment
2. Code quality indicators
3. Suggested improvements"""

        response = await connector.send_message(
            prompt,
            system_prompt="You are a code repository analyst."
        )

        return {
            "analysis": response.get("content", [{}])[0].get("text", ""),
            "analyzed_at": datetime.utcnow().isoformat()
        }

    async def discover_repos(self) -> List[Dict[str, Any]]:
        """
        Auto-discover new Kova AI repositories.

        Returns:
            List of discovered repositories not in config
        """
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.GITHUB_API}/users/{self.github_owner}/repos",
                headers=headers,
                params={"per_page": 100}
            )
            all_repos = response.json()

        # Filter for kova-ai prefix
        prefix = self.config.get(
            "discovery_settings", {}
        ).get("prefix_filter", "kova-ai")

        kova_repos = [
            r for r in all_repos
            if r["name"].lower().startswith(prefix.lower())
        ]

        # Find repos not in config
        configured_names = {r["name"] for r in self.repositories}
        new_repos = [
            r for r in kova_repos
            if r["name"] not in configured_names
        ]

        return new_repos

    def get_status(self) -> Dict[str, Any]:
        """Get sync status for all repositories."""
        return {
            "repositories": self._sync_status,
            "config": {
                "owner": self.github_owner,
                "repo_count": len(self.repositories)
            }
        }
```

---

## Webhook Processing Code

### File: `kova-ai/app/api/webhooks.py` (Extended)

#### Event-Specific Handlers

```python
async def handle_push_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle push event - code pushed to repository.

    Args:
        payload: Push event payload

    Returns:
        Processing result
    """
    commits = payload.get("commits", [])
    branch = payload.get("ref", "").replace("refs/heads/", "")
    repo = payload.get("repository", {}).get("full_name", "")

    # Log push event
    result = {
        "event": "push",
        "repository": repo,
        "branch": branch,
        "commits_count": len(commits),
        "commit_messages": [c.get("message", "") for c in commits[:5]]
    }

    # Store in database
    async with async_session_factory() as session:
        event = WebhookEvent(
            event_type="push",
            payload=payload,
            processed=True
        )
        session.add(event)
        await session.commit()

    return result

async def handle_pull_request_event(
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle pull request events.

    Args:
        payload: PR event payload

    Returns:
        Processing result
    """
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})

    result = {
        "event": "pull_request",
        "action": action,
        "pr_number": pr.get("number"),
        "title": pr.get("title", ""),
        "state": pr.get("state", ""),
        "merged": pr.get("merged", False)
    }

    # Auto-analyze PR on open/synchronize
    if action in ["opened", "synchronize"]:
        connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))
        analysis = await connector.analyze_code(
            pr.get("body", ""),
            analysis_type="full"
        )
        result["ai_analysis"] = analysis

    return result

async def handle_issue_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle issue events."""
    action = payload.get("action", "")
    issue = payload.get("issue", {})

    return {
        "event": "issues",
        "action": action,
        "issue_number": issue.get("number"),
        "title": issue.get("title", ""),
        "state": issue.get("state", "")
    }

async def handle_comment_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle issue comment events."""
    action = payload.get("action", "")
    comment = payload.get("comment", {})
    issue = payload.get("issue", {})

    return {
        "event": "issue_comment",
        "action": action,
        "issue_number": issue.get("number"),
        "comment_id": comment.get("id"),
        "body_preview": comment.get("body", "")[:100]
    }

async def handle_workflow_event(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle workflow run events."""
    workflow = payload.get("workflow_run", {})

    return {
        "event": "workflow_run",
        "workflow_name": workflow.get("name", ""),
        "status": workflow.get("status", ""),
        "conclusion": workflow.get("conclusion", ""),
        "run_number": workflow.get("run_number")
    }
```

---

## Artifact Generation Code

### File: `kova-ai/app/api/artifacts_endpoints.py`

#### Artifact Endpoint Implementations

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from ..services.claude_connector import ClaudeConnector, ArtifactType
import os

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

class CreateArtifactRequest(BaseModel):
    """Request model for artifact creation"""
    artifact_type: str
    prompt: str
    context: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class CodeGenerateRequest(BaseModel):
    """Request model for code generation"""
    description: str
    language: str = "python"
    context: Optional[str] = None
    style: Optional[str] = None  # e.g., "functional", "oop"

class CodeAnalyzeRequest(BaseModel):
    """Request model for code analysis"""
    code: str
    analysis_type: str = "full"  # full, security, performance, bugs

class DocumentGenerateRequest(BaseModel):
    """Request model for document generation"""
    topic: str
    doc_type: str = "readme"  # readme, api-docs, tutorial, changelog
    context: Optional[str] = None

class DiagramGenerateRequest(BaseModel):
    """Request model for diagram generation"""
    description: str
    diagram_type: str = "flowchart"  # flowchart, sequence, class, er
    context: Optional[str] = None

class ConfigGenerateRequest(BaseModel):
    """Request model for config generation"""
    description: str
    format: str = "json"  # json, yaml, toml, ini, xml
    template: Optional[str] = None

@router.post("/create")
async def create_artifact(
    request: CreateArtifactRequest
) -> Dict[str, Any]:
    """
    Create any type of artifact.

    Supported types: code, document, diagram, config, data
    """
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    type_handlers = {
        "code": lambda: connector.generate_code(
            request.prompt,
            request.options.get("language", "python") if request.options else "python"
        ),
        "document": lambda: connector.generate_document(request.prompt),
        "diagram": lambda: connector.generate_diagram(request.prompt),
        "config": lambda: connector.generate_config(
            request.prompt,
            request.options.get("format", "json") if request.options else "json"
        )
    }

    handler = type_handlers.get(request.artifact_type)
    if not handler:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown artifact type: {request.artifact_type}"
        )

    result = await handler()

    # Store artifact
    async with async_session_factory() as session:
        artifact = Artifact(
            artifact_type=request.artifact_type,
            content=result.get("content", [{}])[0].get("text", ""),
            metadata={"prompt": request.prompt, "options": request.options}
        )
        session.add(artifact)
        await session.commit()

    return {"artifact": result, "id": artifact.id}

@router.post("/code/generate")
async def generate_code(request: CodeGenerateRequest) -> Dict[str, Any]:
    """Generate code based on description."""
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    result = await connector.generate_code(
        request.description,
        language=request.language,
        context=request.context
    )

    return {"generated_code": result}

@router.post("/code/analyze")
async def analyze_code(request: CodeAnalyzeRequest) -> Dict[str, Any]:
    """Analyze code for issues and improvements."""
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    result = await connector.analyze_code(
        request.code,
        analysis_type=request.analysis_type
    )

    return {"analysis": result}

@router.post("/document/generate")
async def generate_document(
    request: DocumentGenerateRequest
) -> Dict[str, Any]:
    """Generate markdown documentation."""
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    system_prompts = {
        "readme": "Generate a comprehensive README.md",
        "api-docs": "Generate detailed API documentation",
        "tutorial": "Generate a step-by-step tutorial",
        "changelog": "Generate a CHANGELOG entry"
    }

    system_prompt = system_prompts.get(
        request.doc_type,
        "Generate documentation"
    )

    result = await connector.send_message(
        f"Create {request.doc_type} for: {request.topic}",
        system_prompt=system_prompt
    )

    return {"document": result}

@router.post("/diagram/generate")
async def generate_diagram(
    request: DiagramGenerateRequest
) -> Dict[str, Any]:
    """Generate Mermaid diagram code."""
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""Generate a {request.diagram_type} diagram in Mermaid syntax for:
{request.description}

Return only valid Mermaid code that can be rendered."""

    result = await connector.send_message(
        prompt,
        system_prompt="You are a diagram generation expert. Output only Mermaid syntax."
    )

    return {"diagram": result}

@router.post("/config/generate")
async def generate_config(
    request: ConfigGenerateRequest
) -> Dict[str, Any]:
    """Generate configuration files."""
    connector = ClaudeConnector(os.getenv("ANTHROPIC_API_KEY"))

    format_instructions = {
        "json": "Output valid JSON format",
        "yaml": "Output valid YAML format",
        "toml": "Output valid TOML format",
        "ini": "Output valid INI format",
        "xml": "Output valid XML format"
    }

    prompt = f"""Generate a {request.format} configuration file for:
{request.description}

{format_instructions.get(request.format, '')}
Return only the configuration content, no explanations."""

    result = await connector.send_message(
        prompt,
        system_prompt="You are a configuration file expert."
    )

    return {"config": result}

@router.get("/types")
async def list_artifact_types() -> Dict[str, List[str]]:
    """List all supported artifact types."""
    return {
        "artifact_types": [t.value for t in ArtifactType],
        "code_languages": [
            "python", "javascript", "typescript", "go",
            "rust", "java", "c", "cpp", "ruby", "php"
        ],
        "document_types": ["readme", "api-docs", "tutorial", "changelog"],
        "diagram_types": ["flowchart", "sequence", "class", "er", "gantt"],
        "config_formats": ["json", "yaml", "toml", "ini", "xml"]
    }
```

---

## Service Initialization Code

### File: `kova-ai/app/main.py`

#### FastAPI Application Bootstrap

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

# Import routers
from .api.health import router as health_router
from .api.ai_endpoints import router as ai_router
from .api.webhooks import router as webhooks_router
from .api.multi_repo_endpoints import router as multi_repo_router
from .api.artifacts_endpoints import router as artifacts_router

# Create FastAPI application
app = FastAPI(
    title="Kova AI System API",
    description="AI-powered development automation platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(health_router)
app.include_router(ai_router)
app.include_router(webhooks_router)
app.include_router(multi_repo_router)
app.include_router(artifacts_router)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize database tables
    from .database.session import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Log startup
    import logging
    logging.info("Kova AI System API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    from .database.session import engine
    await engine.dispose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### File: `kovai-ai/claude_bridge_service.py`

#### Async Claude Bridge Service

```python
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import httpx
import os

class ClaudeBridgeService:
    """
    Async bridge service for Claude AI synchronization.
    Runs periodic sync operations in the background.
    """

    SYNC_INTERVAL = 300  # 5 minutes
    CONFIG_PATH = Path("/home/user/Kova-ai-SYSTEM/kova_repos_config.json")

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.is_running = False
        self.last_sync: Dict[str, datetime] = {}

    def _load_repositories(self) -> List[Dict[str, Any]]:
        """Load repository list from config."""
        try:
            with open(self.CONFIG_PATH) as f:
                config = json.load(f)
                return config.get("repositories", [])
        except FileNotFoundError:
            return []

    async def start(self):
        """Start the background sync service."""
        self.is_running = True
        while self.is_running:
            await self._sync_cycle()
            await asyncio.sleep(self.SYNC_INTERVAL)

    async def stop(self):
        """Stop the background sync service."""
        self.is_running = False

    async def _sync_cycle(self):
        """Execute one sync cycle for all repositories."""
        repositories = self._load_repositories()

        for repo in repositories:
            repo_name = repo["name"]
            try:
                await self._sync_repository(repo_name)
                self.last_sync[repo_name] = datetime.utcnow()
            except Exception as e:
                print(f"Sync failed for {repo_name}: {e}")

    async def _sync_repository(self, repo_name: str):
        """Sync a single repository."""
        # Implementation matches MultiRepoSyncService
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get current service status."""
        return {
            "is_running": self.is_running,
            "last_sync": {
                k: v.isoformat() for k, v in self.last_sync.items()
            },
            "sync_interval_seconds": self.SYNC_INTERVAL
        }

# Entry point
if __name__ == "__main__":
    service = ClaudeBridgeService()
    asyncio.run(service.start())
```

---

## Usage Examples

### 1. Making an AI Command Request

```bash
curl -X POST "http://localhost:8000/ai/command" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "analyze",
    "repository": "kova-ai",
    "parameters": {
      "analysis_type": "full"
    }
  }'
```

### 2. Triggering Multi-Repo Sync

```bash
curl -X POST "http://localhost:8000/multi-repo/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "repositories": ["kova-ai", "kova-ai-site"],
    "use_claude": true
  }'
```

### 3. Generating Code Artifact

```bash
curl -X POST "http://localhost:8000/artifacts/code/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A FastAPI endpoint that handles file uploads",
    "language": "python",
    "style": "async"
  }'
```

### 4. Checking Repository Status

```bash
curl -X GET "http://localhost:8000/multi-repo/status"
```

---

## Error Handling Patterns

### Retry with Exponential Backoff

```python
async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 2.0
):
    """
    Retry async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limited
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")
```

### Exception Handling in Endpoints

```python
from fastapi import HTTPException

@router.post("/endpoint")
async def safe_endpoint(request: Request):
    try:
        result = await process_request(request)
        return {"status": "success", "data": result}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ExternalAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
```

---

This code reference provides the complete implementation details for all Kova AI System integrations and services.
