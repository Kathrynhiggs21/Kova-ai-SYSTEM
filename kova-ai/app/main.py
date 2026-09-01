import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import (
    health,
    ai_endpoints,
    webhooks,
    multi_repo_endpoints,
    artifacts_endpoints,
    export_endpoints,
)
from app.security.api_key import require_owner_api_key


def parse_allowed_origins(raw_origins: str) -> list[str]:
    """Parse an explicit, comma-separated browser-origin allowlist."""
    origins = list(
        dict.fromkeys(
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        )
    )
    if "*" in origins:
        raise RuntimeError("KOVA_ALLOWED_ORIGINS must not contain '*'")
    return origins


allowed_origins = parse_allowed_origins(os.getenv("KOVA_ALLOWED_ORIGINS", ""))

app = FastAPI(
    title="Kova AI System API",
    description="Multi-repository AI-powered development automation platform with Claude AI integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=bool(allowed_origins),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "X-Kova-API-Key"],
)

# Routers
app.include_router(health.router)
owner_only = [Depends(require_owner_api_key)]
app.include_router(ai_endpoints.router, dependencies=owner_only)
app.include_router(webhooks.router)
app.include_router(multi_repo_endpoints.router, dependencies=owner_only)
app.include_router(artifacts_endpoints.router, dependencies=owner_only)
app.include_router(export_endpoints.router)

# Metrics
app.mount("/metrics", make_asgi_app())
