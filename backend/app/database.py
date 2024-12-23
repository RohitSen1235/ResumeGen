from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

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
