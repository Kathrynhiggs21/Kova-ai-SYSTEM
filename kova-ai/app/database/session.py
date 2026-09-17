import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def build_default_database_url() -> str:
    return (
        "postgresql+asyncpg://"
        f"{os.getenv('POSTGRES_USER', 'kova')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'kova_pass')}@"
        f"{os.getenv('POSTGRES_HOST', 'db')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'kova')}"
    )


DEFAULT_DATABASE_URL = build_default_database_url()
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()
