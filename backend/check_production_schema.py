#!/usr/bin/env python3
"""
Check Production Schema - Diagnose actual database columns

This script checks what columns actually exist in the production database
to help fix the model mismatch.
"""

import os
import sys
from sqlalchemy import create_engine, text

# Database connection
SQLALCHEMY_DATABASE_URL = "postgresql://resume:postgres@db:5432/resume_builder?connect_timeout=10&application_name=schema_check&client_encoding=utf8"

def check_resumes_table():
    """Check what columns actually exist in the resumes table"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        with engine.connect() as conn:
            print("=== PRODUCTION RESUMES TABLE SCHEMA ===")
            
            # Check if resumes table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='resumes'
            """))
            
            if result.fetchone():
                print("✓ resumes table exists")
                
                # Get all columns in resumes table
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name='resumes'
                    ORDER BY ordinal_position
                """))
                
                print("\nACTUAL columns in resumes table:")
                columns = []
                for row in result:
                    nullable = "NULL" if row[2] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {row[3]}" if row[3] else ""
                    print(f"  - {row[0]}: {row[1]} {nullable}{default}")
                    columns.append(row[0])
                
                print(f"\nColumn list: {columns}")
                
                # Check specifically for content and content_s3_key
                print("\n=== KEY COLUMNS CHECK ===")
                if 'content' in columns:
                    print("✓ content column EXISTS")
                else:
                    print("✗ content column MISSING")
                    
                if 'content_s3_key' in columns:
                    print("✓ content_s3_key column EXISTS")
                else:
                    print("✗ content_s3_key column MISSING")
                    
                # Check current Alembic version
                result = conn.execute(text("""
                    SELECT version_num 
                    FROM alembic_version
                """))
                version = result.fetchone()
                if version:
                    print(f"\n=== ALEMBIC VERSION ===")
                    print(f"Current version: {version[0]}")
                    
                # Count existing resumes
                result = conn.execute(text("SELECT COUNT(*) FROM resumes"))
                count = result.fetchone()
                print(f"\n=== DATA ===")
                print(f"Total resumes: {count[0] if count else 0}")
                    
            else:
                print("✗ resumes table does not exist")
                
    except Exception as e:
        print(f"Error checking schema: {str(e)}")

if __name__ == "__main__":
    check_resumes_table()
