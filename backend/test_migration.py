#!/usr/bin/env python3
"""
Test Migration Script - Check database state before and after migration

This script helps diagnose migration issues by checking the current state
of the database schema and Alembic version history.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
SQLALCHEMY_DATABASE_URL = "postgresql://resume:postgres@db:5432/resume_builder?connect_timeout=10&application_name=test_migration&client_encoding=utf8"

def check_database_state():
    """Check current database schema state"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        with engine.connect() as conn:
            print("=== DATABASE SCHEMA CHECK ===")
            
            # Check if resumes table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='resumes'
            """))
            if result.fetchone():
                print("✓ resumes table exists")
                
                # Check columns in resumes table
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name='resumes'
                    ORDER BY ordinal_position
                """))
                
                print("\nresumes table columns:")
                for row in result:
                    nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {row[3]}" if row[3] else ""
                    print(f"  - {row[0]}: {row[1]} {nullable}{default}")
                    
            else:
                print("✗ resumes table does not exist")
            
            # Check if profiles table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='profiles'
            """))
            if result.fetchone():
                print("\n✓ profiles table exists")
                
                # Check for resume_s3_key column
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='profiles' AND column_name='resume_s3_key'
                """))
                s3_key_col = result.fetchone()
                if s3_key_col:
                    nullable = "NULL" if s3_key_col[2] == 'YES' else "NOT NULL"
                    print(f"  - resume_s3_key: {s3_key_col[1]} {nullable}")
                else:
                    print("  - resume_s3_key: NOT FOUND")
            else:
                print("\n✗ profiles table does not exist")
            
            # Check Alembic version
            result = conn.execute(text("""
                SELECT version_num 
                FROM alembic_version
            """))
            version = result.fetchone()
            if version:
                print(f"\n=== ALEMBIC VERSION ===")
                print(f"Current version: {version[0]}")
            else:
                print("\n✗ No Alembic version found")
                
    except Exception as e:
        print(f"Error checking database state: {str(e)}")

def check_migration_path():
    """Check the migration path from current version to head"""
    print("\n=== MIGRATION PATH ===")
    print("Expected migration order:")
    print("1. bbca5f148aae (add_country_to_educations_table) <- CURRENT")
    print("2. 9a40101fbfdc (add_s3_key_fields_to_profile_and_resume)")
    print("3. fbcbd601f235 (rename_content_to_content_s3_key_in_)")
    print("4. 1dad7cc349e9 (merge_s3_and_profile_branches)")
    print("5. a7aecc9b1fd4 (fix_s3_integration_make_content_and_s3_key_nullable)")

if __name__ == "__main__":
    print("Testing Migration State...")
    check_database_state()
    check_migration_path()
    print("\n=== RECOMMENDATIONS ===")
    print("1. Run 'alembic upgrade head' to apply all pending migrations")
    print("2. The migrations have been updated to handle existing columns safely")
    print("3. If you still get errors, check the specific error message")
