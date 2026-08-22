import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["mcp"])

MCP_API_KEY = os.getenv("MCP_API_KEY")


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
    ]


def _require_mcp_auth(x_api_key: Optional[str]) -> None:
    if MCP_API_KEY and x_api_key != MCP_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "ApiKey"},
        )


@router.get("/mcp")
async def mcp_info(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> Dict[str, Any]:
    _require_mcp_auth(x_api_key)
    return {
        "status": "ok",
        "server": _server_info(),
        "transport": "http-jsonrpc",
    }


@router.post("/mcp", response_model=MCPResponse, response_model_exclude_none=True)
async def mcp_rpc(
    request: MCPRequest,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> MCPResponse:
    _require_mcp_auth(x_api_key)
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
        if not tool_name:
            return MCPResponse(
                id=request.id,
                error={"code": -32602, "message": "Missing required parameter: name"},
            )
        if tool_name == "health_check":
            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": '{"status":"ok"}'}]},
            )
        return MCPResponse(
            id=request.id,
            error={"code": -32602, "message": f"Unknown tool '{tool_name}'"},
        )

    return MCPResponse(
        id=request.id,
        error={"code": -32601, "message": f"Method '{request.method}' not found"},
    )
