from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import health, ai_endpoints, webhooks, scan_endpoints

app = FastAPI()

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
app.include_router(scan_endpoints.router)

# Metrics
app.mount("/metrics", make_asgi_app())
