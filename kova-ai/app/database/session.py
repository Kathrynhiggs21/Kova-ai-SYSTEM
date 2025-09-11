import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def find_project_root(start_path: Path, markers=("pyproject.toml", "setup.py", ".env")) -> Path:
    current = start_path
    while True:
        for marker in markers:
            if (current / marker).exists():
                return current
        if current.parent == current:
            raise FileNotFoundError(f"Project root not found. Looked for markers: {markers}")
        current = current.parent

BASE_DIR = find_project_root(Path(__file__).resolve())
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
