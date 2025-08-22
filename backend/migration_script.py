#!/usr/bin/env python3
"""
S3 Migration Script for ResumeGen

This script migrates:
1. PDF resume files from local filesystem to S3 (profiles.resume_path -> profiles.resume_s3_key)
2. Generated resume content from database to S3 (resumes.content -> resumes.content_s3_key)

Usage:
    docker compose exec backend python migration_script.py
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Add the app directory to Python path
sys.path.append('/app')

from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import create_engine, text
from app.models import Profile, Resume, User
from app.utils.s3_storage import s3_storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/migration.log')
    ]
)
logger = logging.getLogger(__name__)

# Database connection
SQLALCHEMY_DATABASE_URL = "postgresql://resume:postgres@db:5432/resume_builder?connect_timeout=10&application_name=migration_script&client_encoding=utf8"

def get_db_session():
    """Create database session"""
    try:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    except Exception as e:
        logger.error(f"Failed to create database session: {str(e)}")
        raise

def extract_filename_from_path(file_path: str) -> str:
    """Extract filename from file path"""
    return Path(file_path).name

def generate_s3_key_for_resume(user_id: str, profile_id: str, original_filename: str) -> str:
    """Generate S3 key for uploaded resume PDF"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"users/{user_id}/uploaded_resumes/{profile_id}_{timestamp}_{original_filename}"

def generate_s3_key_for_content(user_id: str, resume_id: str) -> str:
    """Generate S3 key for generated resume content"""
    return f"users/{user_id}/generated_resumes/{resume_id}/content.md"

def migrate_resume_files() -> Tuple[int, int]:
    """
    Migrate PDF resume files from local filesystem to S3
    
    Returns:
        Tuple[int, int]: (successful_migrations, failed_migrations)
    """
    logger.info("Starting migration of resume PDF files...")
    
    db = get_db_session()
    successful = 0
    failed = 0
    skipped = 0
    
    try:
        # Query profiles with resume_path but no resume_s3_key, and ensure user exists
        profiles = db.query(Profile).options(joinedload(Profile.user)).filter(
            Profile.resume_path.isnot(None),
            Profile.resume_s3_key.is_(None)
        ).all()
        
        logger.info(f"Found {len(profiles)} profiles with resume files to migrate")
        
        for profile in profiles:
            try:
                # Skip orphaned profiles (no user)
                if not profile.user:
                    logger.warning(f"Skipping orphaned profile {profile.id} (no associated user)")
                    skipped += 1
                    continue
                
                logger.info(f"Processing profile {profile.id} for user {profile.user.email}")
                
                # Check if file exists
                if not os.path.exists(profile.resume_path):
                    logger.warning(f"File not found: {profile.resume_path}")
                    failed += 1
                    continue
                
                # Read file content
                with open(profile.resume_path, 'rb') as file:
                    file_content = file.read()
                
                # Extract original filename
                original_filename = extract_filename_from_path(profile.resume_path)
                
                # Generate S3 key
                s3_key = generate_s3_key_for_resume(
                    str(profile.user_id), 
                    str(profile.id), 
                    original_filename
                )
                
                # Upload to S3
                if s3_storage.upload_file(file_content, s3_key, 'application/pdf'):
                    # Update database
                    profile.resume_s3_key = s3_key
                    db.commit()
                    
                    logger.info(f"Successfully migrated resume for profile {profile.id} to S3: {s3_key}")
                    successful += 1
                else:
                    logger.error(f"Failed to upload resume for profile {profile.id} to S3")
                    failed += 1
                    db.rollback()
                    
            except Exception as e:
                logger.error(f"Error processing profile {profile.id}: {str(e)}")
                failed += 1
                db.rollback()
                
    except Exception as e:
        logger.error(f"Error in migrate_resume_files: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    logger.info(f"Resume files migration completed: {successful} successful, {failed} failed, {skipped} skipped (orphaned)")
    return successful, failed

def migrate_resume_content() -> Tuple[int, int]:
    """
    Migrate generated resume content from database to S3
    
    Returns:
        Tuple[int, int]: (successful_migrations, failed_migrations)
    """
    logger.info("Starting migration of generated resume content...")
    
    db = get_db_session()
    successful = 0
    failed = 0
    skipped = 0
    
    try:
        # First, let's debug what resumes exist
        all_resumes = db.query(Resume).all()
        logger.info(f"Total resumes in database: {len(all_resumes)}")
        
        resumes_with_content = db.query(Resume).filter(
            Resume.content.isnot(None),
            Resume.content != ''
        ).all()
        logger.info(f"Resumes with content: {len(resumes_with_content)}")
        
        # Query resumes with content but no content_s3_key
        resumes = db.query(Resume).options(
            joinedload(Resume.profile).joinedload(Profile.user)
        ).filter(
            Resume.content.isnot(None),
            Resume.content != '',
            Resume.content_s3_key.is_(None)
        ).all()
        
        logger.info(f"Found {len(resumes)} resumes with content to migrate")
        
        # Debug each resume
        for resume in all_resumes:
            content_length = len(resume.content) if resume.content else 0
            logger.info(f"Resume {resume.id}: content_length={content_length}, content_s3_key={resume.content_s3_key}, status={resume.status}")
        
        for resume in resumes:
            try:
                # Skip if profile or user is missing
                if not resume.profile:
                    logger.warning(f"Skipping resume {resume.id} (no associated profile)")
                    skipped += 1
                    continue
                    
                if not resume.profile.user:
                    logger.warning(f"Skipping resume {resume.id} (no associated user)")
                    skipped += 1
                    continue
                
                logger.info(f"Processing resume {resume.id} for user {resume.profile.user.email}")
                logger.info(f"Content length: {len(resume.content)} characters")
                
                # Generate S3 key
                s3_key = generate_s3_key_for_content(
                    str(resume.profile.user_id),
                    str(resume.id)
                )
                
                # Upload content to S3 as markdown file
                content_bytes = resume.content.encode('utf-8')
                if s3_storage.upload_file(content_bytes, s3_key, 'text/markdown'):
                    # Update database
                    resume.content_s3_key = s3_key
                    db.commit()
                    
                    logger.info(f"Successfully migrated content for resume {resume.id} to S3: {s3_key}")
                    successful += 1
                else:
                    logger.error(f"Failed to upload content for resume {resume.id} to S3")
                    failed += 1
                    db.rollback()
                    
            except Exception as e:
                logger.error(f"Error processing resume {resume.id}: {str(e)}")
                failed += 1
                db.rollback()
                
    except Exception as e:
        logger.error(f"Error in migrate_resume_content: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    logger.info(f"Resume content migration completed: {successful} successful, {failed} failed, {skipped} skipped")
    return successful, failed

def verify_s3_connection() -> bool:
    """Verify S3 connection before starting migration"""
    try:
        # First check if we have the required environment variables
        required_env_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION', 'AWS_S3_BUCKET_NAME']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        logger.info(f"Checking S3 connection to bucket: {s3_storage.bucket_name}")
        logger.info(f"Using AWS region: {s3_storage.region}")
        
        # Test S3 connection by attempting to list objects (less restrictive than head_bucket)
        try:
            response = s3_storage.s3_client.list_objects_v2(
                Bucket=s3_storage.bucket_name,
                MaxKeys=1
            )
            logger.info("S3 connection verified successfully")
            return True
        except Exception as list_error:
            logger.warning(f"list_objects_v2 failed: {str(list_error)}")
            # Fallback to head_bucket
            s3_storage.s3_client.head_bucket(Bucket=s3_storage.bucket_name)
            logger.info("S3 connection verified successfully (via head_bucket)")
            return True
            
    except Exception as e:
        logger.error(f"S3 connection failed: {str(e)}")
        logger.error("Please check:")
        logger.error("1. AWS credentials are correctly set in environment variables")
        logger.error("2. S3 bucket exists and is accessible")
        logger.error("3. IAM user has proper permissions for the bucket")
        logger.error("4. Bucket region matches AWS_REGION environment variable")
        return False

def verify_database_connection() -> bool:
    """Verify database connection before starting migration"""
    try:
        db = get_db_session()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection verified successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def print_migration_summary(resume_files_result: Tuple[int, int], content_result: Tuple[int, int]):
    """Print migration summary"""
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Resume Files Migration:")
    print(f"  ✓ Successful: {resume_files_result[0]}")
    print(f"  ✗ Failed: {resume_files_result[1]}")
    print(f"\nResume Content Migration:")
    print(f"  ✓ Successful: {content_result[0]}")
    print(f"  ✗ Failed: {content_result[1]}")
    print(f"\nTotal:")
    print(f"  ✓ Successful: {resume_files_result[0] + content_result[0]}")
    print(f"  ✗ Failed: {resume_files_result[1] + content_result[1]}")
    print("="*60)

def main():
    """Main migration function"""
    logger.info("Starting S3 migration script...")
    
    # Verify connections
    if not verify_database_connection():
        logger.error("Database connection failed. Exiting.")
        sys.exit(1)
    
    if not verify_s3_connection():
        logger.error("S3 connection failed. Exiting.")
        sys.exit(1)
    
    # Perform migrations
    try:
        # Migrate resume files
        resume_files_result = migrate_resume_files()
        
        # Migrate resume content
        content_result = migrate_resume_content()
        
        # Print summary
        print_migration_summary(resume_files_result, content_result)
        
        # Log completion
        total_successful = resume_files_result[0] + content_result[0]
        total_failed = resume_files_result[1] + content_result[1]
        
        if total_failed == 0:
            logger.info("Migration completed successfully with no failures!")
        else:
            logger.warning(f"Migration completed with {total_failed} failures. Check logs for details.")
        
        logger.info("Migration script finished.")
        
    except Exception as e:
        logger.error(f"Migration script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
