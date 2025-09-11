from fastapi import APIRouter, Request

router = APIRouter(prefix="/api/webhooks")


@router.post("/github")
async def github_webhook(request: Request):
    """Echoes received GitHub webhook payload."""
    payload = await request.json()
    return {"received": payload}
