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

def save_generation_status(job_id: str, status: str, progress: int, current_step: str, estimated_time: int = None) -> bool:
    """Save generation status to Redis cache
    
    Args:
        job_id: UUID of the generation job
        status: Current status (parsing, analyzing, optimizing, constructing, completed, failed)
        progress: Progress percentage (0-100)
        current_step: Human-readable description of current step
        estimated_time: Estimated time remaining in seconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client = get_redis()
        pipe = redis_client.pipeline()
        
        # Set all status fields with 30 minute expiration
        pipe.set(f"resume:{job_id}:status", status, ex=1800)
        pipe.set(f"resume:{job_id}:progress", progress, ex=1800)
        pipe.set(f"resume:{job_id}:current_step", current_step, ex=1800)
        
        if estimated_time is not None:
            pipe.set(f"resume:{job_id}:estimated_time", estimated_time, ex=1800)
        
        # Set start time if this is the first status update
        if status == "parsing":
            import time
            pipe.set(f"resume:{job_id}:start_time", int(time.time()), ex=1800)
        
        pipe.execute()
        logger.info(f"Saved generation status for job {job_id}: {status} ({progress}%)")
        return True
    except Exception as e:
        logger.error(f"Failed to save generation status: {str(e)}")
        return False

def get_generation_status(job_id: str) -> dict | None:
    """Get generation status from Redis cache
    
    Args:
        job_id: UUID of the generation job
    
    Returns:
        dict | None: Status information if found, None otherwise
    """
    try:
        redis_client = get_redis()
        pipe = redis_client.pipeline()
        
        pipe.get(f"resume:{job_id}:status")
        pipe.get(f"resume:{job_id}:progress")
        pipe.get(f"resume:{job_id}:current_step")
        pipe.get(f"resume:{job_id}:estimated_time")
        pipe.get(f"resume:{job_id}:start_time")
        
        results = pipe.execute()
        
        if not results[0]:  # No status found
            return None
        
        import time
        current_time = int(time.time())
        start_time = int(results[4]) if results[4] else current_time
        elapsed_time = current_time - start_time
        
        return {
            "status": results[0],
            "progress": int(results[1]) if results[1] else 0,
            "current_step": results[2] or "Processing...",
            "estimated_time_remaining": int(results[3]) if results[3] else None,
            "elapsed_time": elapsed_time,
            "start_time": start_time
        }
    except Exception as e:
        logger.error(f"Failed to get generation status: {str(e)}")
        return None

def save_generation_result(job_id: str, result: dict, expiration: int = 3600) -> bool:
    """Save generation result to Redis cache
    
    Args:
        job_id: UUID of the generation job
        result: Generation result data
        expiration: Cache expiration in seconds (default: 1 hour)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client = get_redis()
        import json
        redis_client.set(f"resume:{job_id}:result", json.dumps(result), ex=expiration)
        logger.info(f"Saved generation result for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to save generation result: {str(e)}")
        return False

def get_generation_result(job_id: str) -> dict | None:
    """Get generation result from Redis cache
    
    Args:
        job_id: UUID of the generation job
    
    Returns:
        dict | None: Generation result if found, None otherwise
    """
    try:
        redis_client = get_redis()
        result_json = redis_client.get(f"resume:{job_id}:result")
        if result_json:
            import json
            return json.loads(result_json)
        return None
    except Exception as e:
        logger.error(f"Failed to get generation result: {str(e)}")
        return None

def cleanup_generation_cache(job_id: str) -> bool:
    """Clean up all cache entries for a generation job
    
    Args:
        job_id: UUID of the generation job
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client = get_redis()
        keys = [
            f"resume:{job_id}:status",
            f"resume:{job_id}:progress", 
            f"resume:{job_id}:current_step",
            f"resume:{job_id}:estimated_time",
            f"resume:{job_id}:start_time",
            f"resume:{job_id}:result",
            f"resume:{job_id}:job_title"
        ]
        redis_client.delete(*keys)
        logger.info(f"Cleaned up cache for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to cleanup generation cache: {str(e)}")
        return False

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
