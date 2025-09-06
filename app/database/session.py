from sqlalchemy.ext.declarative import declarative_base
import os

# For simple operation without async database
ASYNC_DB = False

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/kova")
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Create session maker
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async def get_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    ASYNC_DB = True
                
except ImportError:
    # Fallback for when asyncpg is not available
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    
    # Use SQLite for simple operation
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kova.db")
    
    # Create sync engine
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Create session maker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Create declarative base
Base = declarative_base()