"""Fail-closed owner authentication for KOVA control-plane routes."""

import os
import secrets
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader


owner_api_key_header = APIKeyHeader(name="X-Kova-API-Key", auto_error=False)


def get_owner_api_key() -> str:
    """Return the configured owner API key, if any."""
    return os.getenv("KOVA_OWNER_API_KEY", "").strip()


async def require_owner_api_key(
    supplied_api_key: Optional[str] = Security(owner_api_key_header),
) -> None:
    """Require a valid owner key and reject all traffic when unconfigured."""
    configured_api_key = get_owner_api_key()
    if not configured_api_key or not configured_api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="KOVA owner authentication is not configured",
        )

    if not supplied_api_key or not secrets.compare_digest(
        supplied_api_key, configured_api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing KOVA owner API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
