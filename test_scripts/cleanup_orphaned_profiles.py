#!/usr/bin/env python3
"""
Cleanup Orphaned Profiles Script

This script identifies and removes orphaned profiles (profiles without associated users)
and their related data including resumes, work experiences, educations, skills, projects, etc.

Usage:
    docker compose run --rm backend python test_scripts/cleanup_orphaned_profiles.py

Options:
    --dry-run    Show what would be deleted without actually deleting
    --confirm    Skip confirmation prompt and proceed with deletion
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any

# Add the app directory to Python path
sys.path.append('/app')

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.models import (
    Profile, Resume, User, WorkExperience, Education, 
    Skill, Project, Publication, VolunteerWork
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
SQLALCHEMY_DATABASE_URL = "postgresql://resume:postgres@db:5432/resume_builder?connect_timeout=10&application_name=cleanup_script&client_encoding=utf8"

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

def find_orphaned_profiles() -> List[Dict[str, Any]]:
    """Find all orphaned profiles (profiles without users)"""
    db = get_db_session()
    try:
        # Query to find profiles that don't have corresponding users
        query = """
        SELECT p.id, p.user_id, p.name, p.resume_path, p.created_at
        FROM profiles p 
        LEFT JOIN users u ON p.user_id = u.id 
        WHERE p.user_id IS NOT NULL AND u.id IS NULL
        """
        
        result = db.execute(text(query))
        orphaned_profiles = []
        
        for row in result:
            orphaned_profiles.append({
                'profile_id': row[0],
                'user_id': row[1],
                'name': row[2],
                'resume_path': row[3],
                'created_at': row[4]
            })
        
        return orphaned_profiles
        
    finally:
        db.close()

def get_related_data_counts(profile_id: str) -> Dict[str, int]:
    """Get counts of related data for a profile"""
    db = get_db_session()
    try:
        counts = {}
        
        # Count resumes
        counts['resumes'] = db.query(Resume).filter(Resume.profile_id == profile_id).count()
        
        # Count work experiences
        counts['work_experiences'] = db.query(WorkExperience).filter(WorkExperience.profile_id == profile_id).count()
        
        # Count educations
        counts['educations'] = db.query(Education).filter(Education.profile_id == profile_id).count()
        
        # Count skills
        counts['skills'] = db.query(Skill).filter(Skill.profile_id == profile_id).count()
        
        # Count projects
        counts['projects'] = db.query(Project).filter(Project.profile_id == profile_id).count()
        
        # Count publications
        counts['publications'] = db.query(Publication).filter(Publication.profile_id == profile_id).count()
        
        # Count volunteer works
        counts['volunteer_works'] = db.query(VolunteerWork).filter(VolunteerWork.profile_id == profile_id).count()
        
        return counts
        
    finally:
        db.close()

def delete_orphaned_profile(profile_id: str, dry_run: bool = False) -> Dict[str, int]:
    """Delete an orphaned profile and all its related data"""
    db = get_db_session()
    deleted_counts = {
        'resumes': 0,
        'work_experiences': 0,
        'educations': 0,
        'skills': 0,
        'projects': 0,
        'publications': 0,
        'volunteer_works': 0,
        'profiles': 0
    }
    
    try:
        if not dry_run:
            db.begin()
        
        # Delete resumes
        resumes = db.query(Resume).filter(Resume.profile_id == profile_id).all()
        deleted_counts['resumes'] = len(resumes)
        if not dry_run:
            for resume in resumes:
                db.delete(resume)
        
        # Delete work experiences
        work_experiences = db.query(WorkExperience).filter(WorkExperience.profile_id == profile_id).all()
        deleted_counts['work_experiences'] = len(work_experiences)
        if not dry_run:
            for we in work_experiences:
                db.delete(we)
        
        # Delete educations
        educations = db.query(Education).filter(Education.profile_id == profile_id).all()
        deleted_counts['educations'] = len(educations)
        if not dry_run:
            for edu in educations:
                db.delete(edu)
        
        # Delete skills
        skills = db.query(Skill).filter(Skill.profile_id == profile_id).all()
        deleted_counts['skills'] = len(skills)
        if not dry_run:
            for skill in skills:
                db.delete(skill)
        
        # Delete projects
        projects = db.query(Project).filter(Project.profile_id == profile_id).all()
        deleted_counts['projects'] = len(projects)
        if not dry_run:
            for project in projects:
                db.delete(project)
        
        # Delete publications
        publications = db.query(Publication).filter(Publication.profile_id == profile_id).all()
        deleted_counts['publications'] = len(publications)
        if not dry_run:
            for pub in publications:
                db.delete(pub)
        
        # Delete volunteer works
        volunteer_works = db.query(VolunteerWork).filter(VolunteerWork.profile_id == profile_id).all()
        deleted_counts['volunteer_works'] = len(volunteer_works)
        if not dry_run:
            for vw in volunteer_works:
                db.delete(vw)
        
        # Finally, delete the profile
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        if profile:
            deleted_counts['profiles'] = 1
            if not dry_run:
                db.delete(profile)
        
        if not dry_run:
            db.commit()
            logger.info(f"Successfully deleted orphaned profile {profile_id} and all related data")
        
        return deleted_counts
        
    except Exception as e:
        if not dry_run:
            db.rollback()
        logger.error(f"Error deleting profile {profile_id}: {str(e)}")
        raise
    finally:
        db.close()

def print_summary(orphaned_profiles: List[Dict[str, Any]], dry_run: bool = False):
    """Print summary of orphaned profiles"""
    action = "Would delete" if dry_run else "Found"
    
    print("\n" + "="*80)
    print(f"ORPHANED PROFILES CLEANUP {'(DRY RUN)' if dry_run else ''}")
    print("="*80)
    
    if not orphaned_profiles:
        print("✅ No orphaned profiles found!")
        return
    
    print(f"{action} {len(orphaned_profiles)} orphaned profiles:")
    print()
    
    total_counts = {
        'resumes': 0,
        'work_experiences': 0,
        'educations': 0,
        'skills': 0,
        'projects': 0,
        'publications': 0,
        'volunteer_works': 0,
        'profiles': 0
    }
    
    for i, profile in enumerate(orphaned_profiles, 1):
        print(f"{i}. Profile ID: {profile['profile_id']}")
        print(f"   User ID: {profile['user_id']} (missing)")
        print(f"   Name: {profile['name'] or 'N/A'}")
        print(f"   Resume Path: {profile['resume_path'] or 'N/A'}")
        print(f"   Created: {profile['created_at']}")
        
        # Get related data counts
        counts = get_related_data_counts(profile['profile_id'])
        print(f"   Related data:")
        for data_type, count in counts.items():
            if count > 0:
                print(f"     - {data_type}: {count}")
                total_counts[data_type] += count
        
        total_counts['profiles'] += 1
        print()
    
    print("Summary of data to be deleted:")
    for data_type, count in total_counts.items():
        if count > 0:
            print(f"  - {data_type}: {count}")
    
    print("="*80)

def main():
    """Main cleanup function"""
    parser = argparse.ArgumentParser(description='Cleanup orphaned profiles')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt and proceed with deletion')
    
    args = parser.parse_args()
    
    logger.info("Starting orphaned profiles cleanup...")
    
    # Find orphaned profiles
    orphaned_profiles = find_orphaned_profiles()
    
    # Print summary
    print_summary(orphaned_profiles, dry_run=args.dry_run)
    
    if not orphaned_profiles:
        return
    
    if args.dry_run:
        print("\n🔍 This was a dry run. No data was actually deleted.")
        print("To perform the actual cleanup, run without --dry-run flag.")
        return
    
    # Confirmation prompt
    if not args.confirm:
        print(f"\n⚠️  WARNING: This will permanently delete {len(orphaned_profiles)} orphaned profiles and all their related data!")
        print("This action cannot be undone.")
        
        response = input("\nDo you want to proceed? (type 'yes' to confirm): ").strip().lower()
        if response != 'yes':
            print("❌ Cleanup cancelled.")
            return
    
    # Perform cleanup
    print(f"\n🧹 Cleaning up {len(orphaned_profiles)} orphaned profiles...")
    
    total_deleted = {
        'resumes': 0,
        'work_experiences': 0,
        'educations': 0,
        'skills': 0,
        'projects': 0,
        'publications': 0,
        'volunteer_works': 0,
        'profiles': 0
    }
    
    for profile in orphaned_profiles:
        try:
            deleted_counts = delete_orphaned_profile(profile['profile_id'])
            for key, count in deleted_counts.items():
                total_deleted[key] += count
        except Exception as e:
            logger.error(f"Failed to delete profile {profile['profile_id']}: {str(e)}")
    
    print("\n✅ Cleanup completed!")
    print("Total deleted:")
    for data_type, count in total_deleted.items():
        if count > 0:
            print(f"  - {data_type}: {count}")

if __name__ == "__main__":
    main()
