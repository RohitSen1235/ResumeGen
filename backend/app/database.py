import uuid
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
import redis
from redis import Redis

def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Direct database connection with explicit parameters
SQLALCHEMY_DATABASE_URL = "postgresql://resume:postgres@db:5432/resume_builder?connect_timeout=10&application_name=resume_builder&client_encoding=utf8"

try: 
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    
    # Add engine connection logging
    @event.listens_for(engine, 'connect')
    def receive_connect(dbapi_connection, connection_record):
        logger.info('Database connection established')

except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def get_redis() -> Redis:
    """Get Redis connection"""
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD") or None,
            decode_responses=True
        )
        redis_client.ping()
        logger.info("Redis connection successful")
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise

def save_job_title_to_cache(resume_id: str, job_title: str, expiration: int = 1800) -> bool:
    """Save job title to Redis cache with expiration
    
    Args:
        resume_id: UUID of the resume
        job_title: Job title to cache
        expiration: Cache expiration in seconds (default: 1 day)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client = get_redis()
        key = f"resume:{resume_id}:job_title"
        redis_client.set(key, job_title, ex=expiration)
        logger.info(f"Saved job title to cache for resume {resume_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save job title to cache: {str(e)}")
        return False

def get_job_title_from_cache(resume_id: str) -> str | None:
    """Get job title from Redis cache
    
    Args:
        resume_id: UUID of the resume
    
    Returns:
        str | None: The cached job title if found, None otherwise
    """
    try:
        redis_client = get_redis()
        key = f"resume:{resume_id}:job_title"
        job_title = redis_client.get(key)
        if job_title:
            logger.info(f"Retrieved job title from cache for resume {resume_id}")
            return job_title
        logger.warning(f"No job title found in cache for resume {resume_id}")
        return None
    except Exception as e:
        logger.error(f"Failed to get job title from cache: {str(e)}")
        return None

def cleanup_resumes() -> bool:
    """Delete all resumes from the database
    
    Returns:
        bool: True if successful, False otherwise
    """
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM resumes"))
        db.commit()
        logger.info("Cleared resumes table")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to clear resumes table: {str(e)}")
        return False
    finally:
        db.close()
