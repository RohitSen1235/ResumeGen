#!/usr/bin/env python3
"""
Manual migration management script for development use.
This script provides commands to manage database migrations manually.
"""

import sys
import argparse
import subprocess
import logging
from run_migrations import (
    check_database_connection,
    check_alembic_table_exists,
    get_current_revision,
    get_head_revision,
    check_pending_migrations,
    initialize_alembic,
    run_migrations
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def status():
    """Show migration status"""
    logger.info("Checking migration status...")
    
    if not check_database_connection():
        logger.error("Cannot connect to database")
        return False
    
    if not check_alembic_table_exists():
        logger.warning("Alembic not initialized")
        return False
    
    current = get_current_revision()
    head = get_head_revision()
    
    logger.info(f"Current revision: {current}")
    logger.info(f"Head revision: {head}")
    
    if check_pending_migrations():
        logger.warning("There are pending migrations")
    else:
        logger.info("Database is up to date")
    
    return True

def upgrade():
    """Apply all pending migrations"""
    logger.info("Applying migrations...")
    
    if not check_database_connection():
        logger.error("Cannot connect to database")
        return False
    
    if not check_alembic_table_exists():
        logger.info("Initializing alembic...")
        if not initialize_alembic():
            return False
    
    return run_migrations()

def downgrade(revision="base"):
    """Downgrade to a specific revision"""
    logger.info(f"Downgrading to revision: {revision}")
    
    if not check_database_connection():
        logger.error("Cannot connect to database")
        return False
    
    try:
        result = subprocess.run(
            ['alembic', 'downgrade', revision],
            capture_output=True,
            text=True,
            cwd='/app' if sys.platform != 'win32' else '.'
        )
        
        if result.returncode == 0:
            logger.info("Downgrade completed successfully")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"Downgrade failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error during downgrade: {e}")
        return False

def history():
    """Show migration history"""
    logger.info("Migration history:")
    
    try:
        result = subprocess.run(
            ['alembic', 'history', '--verbose'],
            capture_output=True,
            text=True,
            cwd='/app' if sys.platform != 'win32' else '.'
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            logger.error(f"Error getting history: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return False

def create_migration(message):
    """Create a new migration"""
    logger.info(f"Creating new migration: {message}")
    
    try:
        result = subprocess.run(
            ['alembic', 'revision', '--autogenerate', '-m', message],
            capture_output=True,
            text=True,
            cwd='/app' if sys.platform != 'win32' else '.'
        )
        
        if result.returncode == 0:
            logger.info("Migration created successfully")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"Migration creation failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error creating migration: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Database migration management')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show migration status')
    
    # Upgrade command
    subparsers.add_parser('upgrade', help='Apply all pending migrations')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade to a specific revision')
    downgrade_parser.add_argument('revision', nargs='?', default='base', help='Target revision (default: base)')
    
    # History command
    subparsers.add_parser('history', help='Show migration history')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('message', help='Migration message')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = False
    
    if args.command == 'status':
        success = status()
    elif args.command == 'upgrade':
        success = upgrade()
    elif args.command == 'downgrade':
        success = downgrade(args.revision)
    elif args.command == 'history':
        success = history()
    elif args.command == 'create':
        success = create_migration(args.message)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
