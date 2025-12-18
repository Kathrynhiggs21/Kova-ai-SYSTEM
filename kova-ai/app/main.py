from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import (
    health,
    ai_endpoints,
    webhooks,
    multi_repo_endpoints,
    artifacts_endpoints,
    file_organization_endpoints,
)

app = FastAPI(
    title="Kova AI System API - Kova OS",
    description="Multi-repository AI-powered development automation platform with Claude AI integration, Google Drive file organization, and intelligent automation",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router)
app.include_router(ai_endpoints.router)
app.include_router(webhooks.router)
app.include_router(multi_repo_endpoints.router)
app.include_router(artifacts_endpoints.router)
app.include_router(file_organization_endpoints.router)

# Metrics
app.mount("/metrics", make_asgi_app())
