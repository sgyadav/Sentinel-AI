from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import os
import logging
from pathlib import Path
from core.config import normalize_database_url
from models import Base

logger = logging.getLogger(__name__)

DEFAULT_DATABASE_URL = f"sqlite:///{Path(__file__).with_name('sentinel.db').as_posix()}"
DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))

# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """Get database session with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


# Initialize database tables on startup
def init_db():
    """Initialize all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise
