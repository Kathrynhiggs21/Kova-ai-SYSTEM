from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import SessionLocal
from app.database.models import Repository

router = APIRouter(prefix="/api")

async def get_db():
    """Dependency to get database session"""
    async with SessionLocal() as session:
        yield session

@router.get("/repositories")
async def get_repositories(db: AsyncSession = Depends(get_db)):
    """
    Export all Kova repositories from the database.
    
    Returns a list of all repositories with their id, name, and url.
    """
    result = await db.execute(select(Repository))
    repositories = result.scalars().all()
    
    return {
        "count": len(repositories),
        "repositories": [
            {
                "id": repo.id,
                "name": repo.name,
                "url": repo.url
            }
            for repo in repositories
        ]
    }
