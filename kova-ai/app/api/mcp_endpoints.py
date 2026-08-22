import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["mcp"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SITE_ZIP = PROJECT_ROOT / "site_final.zip"
IMAGES_ZIP = PROJECT_ROOT / "images.zip"


class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int | str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


def _server_info() -> Dict[str, Any]:
    return {
        "name": "kova-mcp-server",
        "version": "1.0.0",
        "url": "https://kovaos.com/mcp",
    }


def _tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "health_check",
            "description": "Returns API health status.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "export_status",
            "description": "Returns KOVA OS export artifact status.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    ]


def _export_status() -> Dict[str, Any]:
    return {
        "site_compiled": SITE_ZIP.exists(),
        "images_compiled": IMAGES_ZIP.exists(),
    }


@router.get("/mcp")
async def mcp_info() -> Dict[str, Any]:
    return {
        "status": "ok",
        "server": _server_info(),
        "transport": "http-jsonrpc",
    }


@router.post("/mcp", response_model=MCPResponse)
async def mcp_rpc(request: MCPRequest) -> MCPResponse:
    if request.method == "initialize":
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": "2024-11-05",
                "serverInfo": _server_info(),
                "capabilities": {"tools": {}},
            },
        )

    if request.method == "tools/list":
        return MCPResponse(id=request.id, result={"tools": _tools()})

    if request.method == "tools/call":
        tool_name = request.params.get("name")
        if tool_name == "health_check":
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": '{"status":"ok"}'}]},
            )
        if tool_name == "export_status":
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": json.dumps(_export_status())}]},
            )
        return MCPResponse(
            id=request.id,
            error={"code": -32602, "message": f"Unknown tool '{tool_name}'"},
        )

    return MCPResponse(
        id=request.id,
        error={"code": -32601, "message": f"Method '{request.method}' not found"},
    )
