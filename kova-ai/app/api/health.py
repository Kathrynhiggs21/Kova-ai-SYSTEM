from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    """Simple health check endpoint."""
    return {"status": "ok"}
