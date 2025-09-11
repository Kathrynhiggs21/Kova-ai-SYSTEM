from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/ai")


@router.post("/command")
async def ai_command(request: Request):
    """Echoes back received AI command payload."""
    data = await request.json()
    return {"received": data}
