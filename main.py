from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from contextlib import asynccontextmanager
import logging, os, time
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest
try:
    from app.api import health, webhooks, ai_endpoints, unzip
    from app.database.session import engine, Base, ASYNC_DB
    IMPORTS_AVAILABLE = True
except Exception as e:
    IMPORTS_AVAILABLE = False

logging.basicConfig(level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
logger = logging.getLogger("kova")

request_count = Counter('kova_requests_total', 'Total HTTP requests', ['method','endpoint','status'])
request_duration = Histogram('kova_request_duration_seconds', 'HTTP request duration')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Kova AI System...")
    try:
        if IMPORTS_AVAILABLE:
            if ASYNC_DB:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("DB initialized (async)")
            else:
                Base.metadata.create_all(bind=engine)
                logger.info("DB initialized (sync)")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    yield
    if IMPORTS_AVAILABLE and ASYNC_DB:
        await engine.dispose()
    logger.info("🛑 Shutdown complete")

app = FastAPI(
    title="Kova AI System",
    description="AI-Powered Dev Automation Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS","*").split(","),
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    dur = time.time() - start
    try:
        request_count.labels(request.method, request.url.path, resp.status_code).inc()
        request_duration.observe(dur)
    except Exception:
        pass
    resp.headers["X-Process-Time"] = f"{dur:.4f}"
    return resp

if IMPORTS_AVAILABLE:
    app.include_router(health.router, tags=["health"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(ai_endpoints.router, prefix="/ai", tags=["ai"])
    app.include_router(unzip.router, prefix="/api", tags=["unzip"])

@app.get("/", tags=["root"])
async def root():
    return {
        "name": "Kova AI System",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {"health": "/health", "metrics": "/metrics", "docs": "/docs"}
    }

@app.get("/metrics", response_class=PlainTextResponse, tags=["monitoring"])
async def metrics():
    return generate_latest()
