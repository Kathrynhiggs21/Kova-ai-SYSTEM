import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DEFAULT_DATABASE_URL = "postgresql+asyncpg://kova:kova_pass@db:5432/kova"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()
