from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api")


class ScanRequest(BaseModel):
    path: str = "."
    max_depth: int = 2


class ScanResponse(BaseModel):
    files: List[str]


@router.post("/scan", response_model=ScanResponse)
async def scan_repository(payload: ScanRequest) -> ScanResponse:
    """Return a list of files under the given path up to max_depth."""
    base = Path(payload.path).resolve()
    if not base.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    files: List[str] = []
    for p in base.rglob("*"):
        if p.is_file() and len(p.relative_to(base).parts) <= payload.max_depth:
            files.append(str(p.relative_to(base)))

    return ScanResponse(files=files)
