from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./sentinel.db"

# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


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