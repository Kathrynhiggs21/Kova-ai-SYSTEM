"""
Artifacts API Endpoints

Manages Claude-generated artifacts (code, documents, diagrams, configs)
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import APIRouter, HTTPException  # noqa: E402
from pydantic import BaseModel  # noqa: E402
from typing import Optional, Dict, Any  # noqa: E402

from services.claude_connector import ClaudeConnector, ArtifactType  # noqa: E402

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


class CreateArtifactRequest(BaseModel):
    name: str
    artifact_type: ArtifactType
    description: str
    context: Optional[Dict[str, Any]] = None
    repository: Optional[str] = None


class GenerateCodeRequest(BaseModel):
    description: str
    language: str = "python"
    context: Optional[str] = None


class AnalyzeCodeRequest(BaseModel):
    code: str
    language: str = "python"
    focus: Optional[str] = None


class ArtifactResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None


@router.post("/create", response_model=ArtifactResponse)
async def create_artifact(request: CreateArtifactRequest):
    """
    Create an artifact using Claude AI

    Supports:
    - Code generation
    - Documentation
    - Diagrams (Mermaid)
    - Configuration files
    """
    try:
        connector = ClaudeConnector()

        result = await connector.create_artifact(
            name=request.name,
            artifact_type=request.artifact_type,
            description=request.description,
            context=request.context,
        )

        return ArtifactResponse(
            success=result.get("success", False), data=result, error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/generate", response_model=ArtifactResponse)
async def generate_code(request: GenerateCodeRequest):
    """
    Generate code using Claude AI

    Example:
    ```json
    {
        "description": "Create a function to calculate factorial",
        "language": "python"
    }
    ```
    """
    try:
        connector = ClaudeConnector()

        result = await connector.generate_code(
            description=request.description,
            language=request.language,
            context=request.context,
        )

        return ArtifactResponse(
            success=result.get("success", False), data=result, error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code/analyze", response_model=ArtifactResponse)
async def analyze_code(request: AnalyzeCodeRequest):
    """
    Analyze code using Claude AI

    Provides insights on:
    - Potential bugs
    - Security issues
    - Performance
    - Best practices
    """
    try:
        connector = ClaudeConnector()

        result = await connector.analyze_code(
            code=request.code, language=request.language, focus=request.focus
        )

        return ArtifactResponse(
            success=result.get("success", False), data=result, error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/document/generate", response_model=ArtifactResponse)
async def generate_document(
    title: str, description: str, context: Optional[Dict] = None
):
    """
    Generate markdown documentation using Claude AI
    """
    try:
        connector = ClaudeConnector()

        result = await connector.generate_document(
            title=title, description=description, context=context
        )

        return ArtifactResponse(
            success=result.get("success", False), data=result, error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagram/generate", response_model=ArtifactResponse)
async def generate_diagram(description: str, context: Optional[Dict] = None):
    """
    Generate Mermaid diagram using Claude AI

    Example:
    ```json
    {
        "description": "Create a flowchart showing the user authentication process"
    }
    ```
    """
    try:
        connector = ClaudeConnector()

        result = await connector.generate_diagram(
            description=description, context=context
        )

        return ArtifactResponse(
            success=result.get("success", False), data=result, error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/generate", response_model=ArtifactResponse)
async def generate_config(
    description: str, config_format: str = "json", context: Optional[Dict] = None
):
    """
    Generate configuration file using Claude AI

    Supported formats:
    - json
    - yaml
    - toml
    - ini
    """
    try:
        connector = ClaudeConnector()

        ctx = context or {}
        ctx["format"] = config_format

        result = await connector.generate_config(description=description, context=ctx)

        return ArtifactResponse(
            success=result.get("success", False), data=result, error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_artifact_types():
    """Get list of supported artifact types"""
    return {
        "artifact_types": [
            {
                "type": "code",
                "description": "Generate code in any programming language",
            },
            {"type": "document", "description": "Generate markdown documentation"},
            {"type": "diagram", "description": "Generate Mermaid diagrams"},
            {"type": "config", "description": "Generate configuration files"},
            {"type": "data", "description": "Generate data structures"},
        ],
        "supported_languages": [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "c",
            "cpp",
            "csharp",
            "ruby",
            "php",
            "swift",
            "kotlin",
            "scala",
            "r",
            "sql",
        ],
        "supported_config_formats": ["json", "yaml", "toml", "ini", "xml"],
    }
