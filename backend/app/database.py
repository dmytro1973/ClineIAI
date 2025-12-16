from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from typing import AsyncGenerator, Optional
import logging

from .config import settings
from .db_base import Base

# Configure logging
logger = logging.getLogger(__name__)

# Database engine
engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None

async def close_db() -> None:
    """Dispose the engine and reset globals.

    This is important on Windows + aiosqlite, where open pooled connections may
    keep background threads alive.
    """
    global engine, AsyncSessionLocal

    if engine is not None:
        await engine.dispose()

    engine = None
    AsyncSessionLocal = None

def init_db() -> None:
    """Initialize database engine and session factory"""
    global engine, AsyncSessionLocal

    if engine is None:
        logger.info("Initializing database engine...")
        database_url = settings.get_database_url()
        logger.debug(f"Database URL: {database_url}")

        # Determine if using SQLite
        is_sqlite = "sqlite" in database_url

        # Create async engine with appropriate settings
        if is_sqlite:
            # SQLite/aiosqlite does NOT support pool_size, max_overflow, pool_pre_ping, pool_recycle
            engine = create_async_engine(
                database_url,
                echo=settings.app.debug,
                connect_args={"check_same_thread": False}
            )
        else:
            # PostgreSQL/MySQL etc. support connection pooling
            engine = create_async_engine(
                database_url,
                echo=settings.app.debug,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
            )

        # Create async session factory
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )

        logger.info("Database engine initialized successfully")

async def create_tables() -> None:
    """Create all database tables"""
    if engine is None:
        init_db()

    # Import models lazily here to ensure Base.metadata is populated
    # without causing circular imports during module initialization.
    from . import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

async def drop_tables() -> None:
    """Drop all database tables"""
    if engine is None:
        init_db()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async SQLAlchemy session."""
    if AsyncSessionLocal is None:
        init_db()

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise

def get_sync_engine():
    """Get synchronous engine for Alembic migrations"""
    from sqlalchemy import create_engine
    database_url = settings.get_database_url().replace("sqlite+aiosqlite", "sqlite")
    return create_engine(database_url, connect_args={"check_same_thread": False})

# NOTE:
# We intentionally do NOT initialize the database engine on module import.
# This avoids import-time side effects and makes it possible to import the app
# (e.g. for tooling/tests) even if the DB driver isn't installed yet.

if __name__ == "__main__":
    import asyncio

    async def test_db():
        """Test database connection"""
        try:
            async for db in get_db():
                # Test simple query
                result = await db.execute("SELECT 1")
                row = result.fetchone()
                if row and row[0] == 1:
                    print("✅ Database connection successful!")
                else:
                    print("❌ Database connection failed")
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")

    asyncio.run(test_db())
