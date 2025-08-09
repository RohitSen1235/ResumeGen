#!/usr/bin/env python3
"""
Script to automatically check and apply database migrations using Alembic.
This script will:
1. Check if there are pending migrations
2. Apply them if they exist
3. Handle errors gracefully
"""

import sys
import logging
import subprocess
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, ProgrammingError
from app.database import SQLALCHEMY_DATABASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if database is accessible"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def check_alembic_table_exists():
    """Check if alembic_version table exists"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return 'alembic_version' in tables
    except Exception as e:
        logger.error(f"Error checking alembic table: {e}")
        return False

def get_current_revision():
    """Get current database revision"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version_num FROM alembic_version'))
            current_rev = result.scalar()
            logger.info(f"Current database revision: {current_rev}")
            return current_rev
    except (OperationalError, ProgrammingError) as e:
        logger.warning(f"Could not get current revision (table might not exist): {e}")
        return None
    except Exception as e:
        logger.error(f"Error getting current revision: {e}")
        return None

def get_head_revision():
    """Get the latest revision from migration files"""
    try:
        result = subprocess.run(
            ['alembic', 'heads'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        if result.returncode == 0:
            head_rev = result.stdout.strip()
            logger.info(f"Head revision: {head_rev}")
            return head_rev
        else:
            logger.error(f"Error getting head revision: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error running alembic heads: {e}")
        return None

def check_pending_migrations():
    """Check if there are pending migrations"""
    try:
        result = subprocess.run(
            ['alembic', 'current'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        
        if result.returncode != 0:
            logger.error(f"Error checking current revision: {result.stderr}")
            return True  # Assume migrations needed if we can't check
        
        current_output = result.stdout.strip()
        
        # Get head revision
        head_result = subprocess.run(
            ['alembic', 'heads'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        
        if head_result.returncode != 0:
            logger.error(f"Error getting head revision: {head_result.stderr}")
            return True
        
        head_output = head_result.stdout.strip()
        
        # Compare current and head
        if current_output != head_output:
            logger.info("Pending migrations detected")
            return True
        else:
            logger.info("Database is up to date")
            return False
            
    except Exception as e:
        logger.error(f"Error checking pending migrations: {e}")
        return True  # Assume migrations needed on error

def initialize_alembic():
    """Initialize alembic if not already initialized"""
    try:
        logger.info("Initializing alembic...")
        result = subprocess.run(
            ['alembic', 'stamp', 'head'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        
        if result.returncode == 0:
            logger.info("Alembic initialized successfully")
            return True
        else:
            logger.error(f"Error initializing alembic: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error initializing alembic: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    try:
        logger.info("Running database migrations...")
        result = subprocess.run(
            ['alembic', 'upgrade', 'a154f7786dff'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully")
            logger.info(f"Migration output: {result.stdout}")
            return True
        else:
            logger.error(f"Migration failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False

def main():
    """Main function to check and apply migrations"""
    logger.info("Starting migration check and application process...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Cannot connect to database. Exiting.")
        sys.exit(1)
    
    # Check if alembic is initialized
    if not check_alembic_table_exists():
        logger.info("Alembic not initialized. Initializing...")
        if not initialize_alembic():
            logger.error("Failed to initialize alembic. Exiting.")
            sys.exit(1)
    
    # Check for pending migrations
    if check_pending_migrations():
        logger.info("Applying pending migrations...")
        if not run_migrations():
            logger.error("Failed to apply migrations. Exiting.")
            sys.exit(1)
    else:
        logger.info("No pending migrations found.")
    
    logger.info("Migration process completed successfully!")

if __name__ == "__main__":
    main()
