from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.config import config
from utils.logger import logger
import os


def _normalize_database_url(url: str) -> str:
    """Normalize DATABASE_URL for SQLAlchemy/psycopg2 and ensure SSL for Railway.
    - Convert postgres:// → postgresql+psycopg2://
    - Convert postgresql:// → postgresql+psycopg2://
    - Append sslmode=require if not present (default True when using Railway)
    """
    if not url:
        raise ValueError("DATABASE_URL is not set")

    normalized = url
    if normalized.startswith("postgres://"):
        normalized = normalized.replace("postgres://", "postgresql+psycopg2://", 1)
    elif normalized.startswith("postgresql://"):
        normalized = normalized.replace("postgresql://", "postgresql+psycopg2://", 1)

    requires_ssl = os.getenv("DB_SSLMODE_REQUIRE", "1") == "1" or ("railway" in normalized)
    if "sslmode=" not in normalized and requires_ssl:
        delimiter = "?" if "?" not in normalized else "&"
        normalized = f"{normalized}{delimiter}sslmode=require"

    return normalized


# Create SQLAlchemy engine
engine = create_engine(
    _normalize_database_url(config.DATABASE_URL),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Import models to ensure they're registered with Base
        from .models import Paper, Chunk, ClusterResult, Hypothesis, ExperimentPlan
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def test_db_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
