"""Database configuration and session management"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from core.config import get_settings
from .base import Base

logger = logging.getLogger(__name__)
settings = get_settings()

# Create database engine
# Use StaticPool for SQLite in-memory databases
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    poolclass=StaticPool if "sqlite:///:memory:" in settings.DATABASE_URL else None,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """
    Database session dependency for FastAPI
    Yields a database session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def drop_db():
    """Drop all database tables (USE WITH CAUTION - FOR TESTING ONLY)"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database tables dropped")
