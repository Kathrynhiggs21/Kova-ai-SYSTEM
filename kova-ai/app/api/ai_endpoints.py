from fastapi import APIRouter, Request

router = APIRouter(prefix="/ai")

@router.post("/command")
async def ai_command(request: Request):
    data = await request.json()
    # Basic echo for now
    return {"received": data}
