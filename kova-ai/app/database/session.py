import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
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


def resolve_database_url() -> str:
    """Resolve a real DSN, ignoring copied template placeholders."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url or "<" in database_url or ">" in database_url:
        return build_default_database_url()
    return database_url


def is_sqlalchemy_echo_enabled() -> bool:
    """Return whether SQLAlchemy should log emitted SQL statements."""
    return os.getenv("SQLALCHEMY_ECHO", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def create_database_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine from the current environment."""
    return create_async_engine(
        resolve_database_url(),
        echo=is_sqlalchemy_echo_enabled(),
    )


DEFAULT_DATABASE_URL = build_default_database_url()
engine = create_database_engine()
DATABASE_URL = engine.url.render_as_string(hide_password=False)
SessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()
