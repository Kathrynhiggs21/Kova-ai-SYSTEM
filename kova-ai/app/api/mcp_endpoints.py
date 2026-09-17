"""Authenticated Model Context Protocol (MCP) HTTP endpoint for KOVA."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.security.api_key import require_owner_api_key
from app.services.multi_repo_sync_service import MultiRepoSyncService


router = APIRouter(
    prefix="/mcp",
    tags=["mcp"],
    dependencies=[Depends(require_owner_api_key)],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SITE_ZIP = PROJECT_ROOT / "site_final.zip"
IMAGES_ZIP = PROJECT_ROOT / "images.zip"

TOOLS = [
    {
        "name": "kova_health",
        "description": "Return the health status of the KOVA API.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "kova_export_status",
        "description": "Return the status of the published KOVA export archives.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "kova_list_repositories",
        "description": "List repositories enabled in the KOVA registry.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "kova_repository_status",
        "description": "Return live GitHub metadata for configured KOVA repositories.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]


def _export_status() -> dict[str, Any]:
    def archive_status(path: Path) -> dict[str, Any]:
        exists = path.exists()
        return {
            "compiled": exists,
            "size_kb": round(path.stat().st_size / 1024, 2) if exists else 0.0,
            "last_modified": (
                datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                if exists
                else None
            ),
        }

    return {"site": archive_status(SITE_ZIP), "images": archive_status(IMAGES_ZIP)}


async def _call_tool(name: str, arguments: dict[str, Any]) -> Any:
    if arguments:
        raise ValueError(f"{name} does not accept arguments")
    if name == "kova_health":
        return {"status": "ok"}
    if name == "kova_export_status":
        return _export_status()
    if name == "kova_list_repositories":
        repositories = MultiRepoSyncService().get_enabled_repos()
        return {"repositories": repositories, "count": len(repositories)}
    if name == "kova_repository_status":
        return await MultiRepoSyncService().get_cross_repo_status()
    raise KeyError(name)


def _success(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


@router.post("")
async def mcp_message(message: dict[str, Any]) -> dict[str, Any] | None:
    """Handle MCP JSON-RPC messages over Streamable HTTP's JSON transport."""
    request_id = message.get("id")
    if message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        raise HTTPException(status_code=400, detail="Invalid JSON-RPC 2.0 message")

    method = message["method"]
    params = message["params"] if "params" in message else {}
    if params is None or not isinstance(params, dict):
        return _error(request_id, -32602, "params must be an object")

    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _success(
            request_id,
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "kova-ai-system", "version": "2.0.0"},
            },
        )
    if method == "ping":
        return _success(request_id, {})
    if method == "tools/list":
        return _success(request_id, {"tools": TOOLS})
    if method != "tools/call":
        return _error(request_id, -32601, f"Method not found: {method}")

    name = params.get("name")
    arguments = params.get("arguments") or {}
    if not isinstance(name, str) or not isinstance(arguments, dict):
        return _error(request_id, -32602, "tools/call requires a name and object arguments")
    try:
        result = await _call_tool(name, arguments)
    except KeyError:
        return _error(request_id, -32602, f"Unknown tool: {name}")
    except ValueError:
        return _error(request_id, -32602, "Tool arguments are not supported")
    except Exception:
        return _error(request_id, -32603, "Tool execution failed")

    return _success(
        request_id,
        {"content": [{"type": "text", "text": json.dumps(result, sort_keys=True)}]},
    )
