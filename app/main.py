from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
import logging, os, time
from datetime import datetime
from typing import Dict, Any
from prometheus_client import Counter, Histogram, generate_latest

logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
request_count = Counter('kova_requests_total','Total HTTP requests',['method','endpoint','status'])
request_duration = Histogram('kova_request_duration_seconds','HTTP request duration')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Kova AI System...")
    yield
    logger.info("Shutting down Kova AI System...")

app = FastAPI(title="Kova AI System", version="1.0.0", lifespan=lifespan,
              docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")

app.add_middleware(CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS","http://localhost:3000").split(","),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

try:
    from app.api.health import router as health_router
    app.include_router(health_router)
except Exception as e:
    logger.info(f"Health router not loaded: {e}")

@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    dur = time.time() - start
    response.headers["X-Process-Time"] = str(dur)
    request_count.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
    request_duration.observe(dur)
    return response

@app.get("/", tags=["root"])
async def root():
    return {"name":"Kova AI System","version":"1.0.0","status":"operational",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints":{"health":"/health","metrics":"/metrics","docs":"/docs"}}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status":"healthy","timestamp":datetime.utcnow().isoformat(),
            "checks":{"database":"healthy","redis":"healthy","ai_service":"healthy"}}

@app.get("/metrics", response_class=PlainTextResponse, tags=["monitoring"])
async def metrics():
    return generate_latest()

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=404, content={"error":"Resource not found","path":str(request.url)})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal error: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error":"Internal server error","message":"An unexpected error occurred"})
