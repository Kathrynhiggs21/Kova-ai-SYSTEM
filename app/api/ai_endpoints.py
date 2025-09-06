from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
router = APIRouter()
class Command(BaseModel):
    command: str
@router.post("/command")
async def command(req: Command):
    return {"status":"processing","command":req.command,"timestamp":datetime.utcnow().isoformat()}
