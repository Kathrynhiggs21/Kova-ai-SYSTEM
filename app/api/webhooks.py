from fastapi import APIRouter, Request
router = APIRouter()
@router.post("/github")
async def github(request: Request):
    event = request.headers.get("X-GitHub-Event","unknown")
    payload = await request.json()
    return {"status":"accepted","event":event}
