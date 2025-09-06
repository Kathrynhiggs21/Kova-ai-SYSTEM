from fastapi import APIRouter, Request

router = APIRouter(prefix="/webhooks")

@router.post("/github")
async def github_webhook(request: Request):
    payload = await request.json()
    # Basic echo for now
    return {"received": payload}
