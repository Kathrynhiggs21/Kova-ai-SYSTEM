import os
import httpx
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

router = APIRouter(prefix="/ai")

class ClaudeCommand(BaseModel):
    command: str
    repository: Optional[str] = None
    file_path: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    action: str = "analyze"  # analyze, sync, process, webhook

class ClaudeResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    claude_response: Optional[str] = None
    repository_info: Optional[Dict[str, Any]] = None

@router.post("/command", response_model=ClaudeResponse)
async def ai_command(command: ClaudeCommand):
    try:
        if command.action == "sync":
            return await sync_with_claude(command)
        elif command.action == "analyze":
            return await analyze_repository(command)
        elif command.action == "process":
            return await process_github_data(command)
        else:
            return await execute_general_command(command)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def sync_with_claude(command: ClaudeCommand) -> ClaudeResponse:
    """Sync repository data with Claude"""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not anthropic_key:
        raise HTTPException(status_code=400, detail="Anthropic API key not configured")
    
    # Fetch repository data
    repo_data = await fetch_repository_data(command.repository, github_token)
    
    # Send to Claude
    claude_response = await send_to_claude(repo_data, command.command, anthropic_key)
    
    return ClaudeResponse(
        status="success",
        data={"sync_completed": True, "repository": command.repository},
        claude_response=claude_response,
        repository_info=repo_data
    )

async def analyze_repository(command: ClaudeCommand) -> ClaudeResponse:
    """Analyze repository structure and content"""
    github_token = os.getenv("GITHUB_TOKEN")
    
    repo_data = await fetch_repository_data(command.repository, github_token)
    
    analysis = {
        "structure": await get_repository_structure(command.repository, github_token),
        "recent_commits": await get_recent_commits(command.repository, github_token),
        "file_content": await get_file_content(command.repository, command.file_path, github_token) if command.file_path else None
    }
    
    return ClaudeResponse(
        status="success",
        data=analysis,
        repository_info=repo_data
    )

async def process_github_data(command: ClaudeCommand) -> ClaudeResponse:
    """Process GitHub data for Claude consumption"""
    github_token = os.getenv("GITHUB_TOKEN")
    
    processed_data = {
        "repositories": await get_user_repositories("Kathrynhiggs21", github_token),
        "kova_repos": await get_kova_repositories(github_token),
        "latest_activity": await get_latest_activity("Kathrynhiggs21", github_token)
    }
    
    return ClaudeResponse(
        status="success",
        data=processed_data
    )

async def execute_general_command(command: ClaudeCommand) -> ClaudeResponse:
    """Execute general AI commands"""
    return ClaudeResponse(
        status="success",
        data={"command": command.command, "context": command.context},
        claude_response=f"Processed command: {command.command}"
    )

async def fetch_repository_data(repository: str, github_token: str) -> Dict[str, Any]:
    """Fetch comprehensive repository data from GitHub API"""
    if not repository:
        repository = "Kathrynhiggs21/Kova-ai-SYSTEM"
    
    headers = {"Authorization": f"token {github_token}"}
    
    async with httpx.AsyncClient() as client:
        # Basic repo info
        repo_response = await client.get(f"https://api.github.com/repos/{repository}", headers=headers)
        repo_data = repo_response.json()
        
        # Repository contents
        contents_response = await client.get(f"https://api.github.com/repos/{repository}/contents", headers=headers)
        contents_data = contents_response.json() if contents_response.status_code == 200 else []
        
        return {
            "repository": repo_data,
            "contents": contents_data,
            "timestamp": "2025-10-20 14:38:05"
        }

async def get_repository_structure(repository: str, github_token: str) -> Dict[str, Any]:
    """Get repository file structure"""
    headers = {"Authorization": f"token {github_token}"}
    
    async with httpx.AsyncClient() as client:
        tree_response = await client.get(f"https://api.github.com/repos/{repository}/git/trees/main?recursive=1", headers=headers)
        return tree_response.json() if tree_response.status_code == 200 else {}

async def get_recent_commits(repository: str, github_token: str) -> Dict[str, Any]:
    """Get recent commits"""
    headers = {"Authorization": f"token {github_token}"}
    
    async with httpx.AsyncClient() as client:
        commits_response = await client.get(f"https://api.github.com/repos/{repository}/commits?per_page=10", headers=headers)
        return commits_response.json() if commits_response.status_code == 200 else []

async def get_file_content(repository: str, file_path: str, github_token: str) -> Dict[str, Any]:
    """Get specific file content"""
    headers = {"Authorization": f"token {github_token}"}
    
    async with httpx.AsyncClient() as client:
        file_response = await client.get(f"https://api.github.com/repos/{repository}/contents/{file_path}", headers=headers)
        return file_response.json() if file_response.status_code == 200 else {}

async def get_user_repositories(username: str, github_token: str) -> Dict[str, Any]:
    """Get all user repositories"""
    headers = {"Authorization": f"token {github_token}"}
    
    async with httpx.AsyncClient() as client:
        repos_response = await client.get(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
        return repos_response.json() if repos_response.status_code == 200 else []

async def get_kova_repositories(github_token: str) -> Dict[str, Any]:
    """Get Kova-specific repositories"""
    headers = {"Authorization": f"token {github_token}"}
    kova_repos = [
        "Kathrynhiggs21/Kova-ai-SYSTEM",
        "Kathrynhiggs21/kova-ai",
        "Kathrynhiggs21/kova-ai-site",
        "Kathrynhiggs21/kova-ai-mem0",
        "Kathrynhiggs21/Kova-AI-Scribbles"
    ]
    
    repo_data = {}
    async with httpx.AsyncClient() as client:
        for repo in kova_repos:
            response = await client.get(f"https://api.github.com/repos/{repo}", headers=headers)
            if response.status_code == 200:
                repo_data[repo] = response.json()
    
    return repo_data

async def get_latest_activity(username: str, github_token: str) -> Dict[str, Any]:
    """Get latest user activity"""
    headers = {"Authorization": f"token {github_token}"}
    
    async with httpx.AsyncClient() as client:
        events_response = await client.get(f"https://api.github.com/users/{username}/events?per_page=20", headers=headers)
        return events_response.json() if events_response.status_code == 200 else []

async def send_to_claude(data: Dict[str, Any], prompt: str, anthropic_key: str) -> str:
    """Send data to Claude API"""
    headers = {
        "Authorization": f"Bearer {anthropic_key}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 4000,
        "messages": [
            {
                "role": "user",
                "content": f"Repository data: {json.dumps(data, indent=2)}\n\nUser request: {prompt}"
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result.get("content", [{}])[0].get("text", "No response from Claude")
        else:
            return f"Error communicating with Claude: {response.status_code}"