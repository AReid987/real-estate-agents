"""
Database connection for API Gateway
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import structlog
from config import settings

logger = structlog.get_logger()

# Database engine and session
engine = None
async_session_maker = None

async def init_database():
    """Initialize database connection"""
    global engine, async_session_maker
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=True if settings.log_level == "DEBUG" else False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300
        )
        
        # Create session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("API Gateway database connection established")
        
    except Exception as e:
        logger.error("Failed to initialize API database", error=str(e))
        raise

async def get_session() -> AsyncSession:
    """Get database session"""
    if not async_session_maker:
        raise RuntimeError("Database not initialized")
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()