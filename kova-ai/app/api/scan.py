from fastapi import APIRouter, Request

router = APIRouter(prefix="/api")


@router.post("/scan")
async def scan_repository(request: Request):
    data = await request.json()
    repo_name = data.get("name", "unknown")
    # Placeholder implementation
    return {"status": "scanning", "repository": repo_name}
