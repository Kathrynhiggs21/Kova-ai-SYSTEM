from fastapi import APIRouter
router = APIRouter(tags=["health"])
@router.get("/healthz")
def hz():
    return {"ok": True}
