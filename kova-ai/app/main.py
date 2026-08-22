from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_asgi_app

from app.api import (
    health,
    ai_endpoints,
    webhooks,
    multi_repo_endpoints,
    artifacts_endpoints,
    export_endpoints,
    mcp_endpoints,
)

app = FastAPI(
    title="Kova AI System API",
    description="Multi-repository AI-powered development automation platform with Claude AI integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

web_root = Path(__file__).resolve().parent / "static" / "kovaos"

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
app.include_router(export_endpoints.router)
app.include_router(mcp_endpoints.router)

# Metrics
app.mount("/metrics", make_asgi_app())

if web_root.exists():
    app.mount("/static", StaticFiles(directory=web_root), name="kovaos-static")


@app.get("/", include_in_schema=False)
async def kovaos_home():
    return FileResponse(web_root / "index.html")


@app.get("/dashboard", include_in_schema=False)
@app.get("/dashboard/{subpath:path}", include_in_schema=False)
async def kovaos_dashboard(subpath: str = ""):
    return FileResponse(web_root / "dashboard.html")
