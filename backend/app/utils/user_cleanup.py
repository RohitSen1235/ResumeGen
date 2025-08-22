import logging
import os
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models import User, Profile, Resume, WorkExperience, Education, Skill, Project, Publication, VolunteerWork
from .s3_storage import s3_storage

logger = logging.getLogger(__name__)

class UserDataCleanup:
    """Utility class for complete user data cleanup including S3 files"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def delete_user_completely(self, user_id: str) -> Dict[str, Any]:
        """
        Completely delete a user and all associated data including:
        - Profile and all profile sections (work experience, education, skills, etc.)
        - All resumes and their S3 content
        - Uploaded resume files (both local and S3)
        - All database records
        
        Returns a summary of what was deleted.
        """
        try:
            # Get the user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found", "deleted": {}}
            
            deletion_summary = {
                "user_id": str(user_id),
                "user_email": user.email,
                "deleted": {
                    "profile": False,
                    "resumes": 0,
                    "resume_s3_files": 0,
                    "uploaded_resume_file": False,
                    "uploaded_resume_s3_file": False,
                    "work_experiences": 0,
                    "educations": 0,
                    "skills": 0,
                    "projects": 0,
                    "publications": 0,
                    "volunteer_works": 0,
                    "local_files_deleted": [],
                    "s3_files_deleted": [],
                    "s3_deletion_errors": []
                }
            }
            
            # Get profile if exists
            profile = user.profile
            if profile:
                deletion_summary["deleted"]["profile"] = True
                
                # Note: resume_path field has been removed - resumes are now stored in S3 only
                
                # Delete uploaded resume from S3
                if profile.resume_s3_key:
                    try:
                        if s3_storage.delete_file(profile.resume_s3_key):
                            deletion_summary["deleted"]["uploaded_resume_s3_file"] = True
                            deletion_summary["deleted"]["s3_files_deleted"].append(profile.resume_s3_key)
                            logger.info(f"Deleted S3 resume file: {profile.resume_s3_key}")
                        else:
                            deletion_summary["deleted"]["s3_deletion_errors"].append(f"Failed to delete resume S3 file: {profile.resume_s3_key}")
                    except Exception as e:
                        logger.error(f"Error deleting S3 resume file {profile.resume_s3_key}: {str(e)}")
                        deletion_summary["deleted"]["s3_deletion_errors"].append(f"Error deleting resume S3 file: {str(e)}")
                
                # Delete all resume S3 content
                resumes = self.db.query(Resume).filter(Resume.profile_id == profile.id).all()
                for resume in resumes:
                    if resume.content_s3_key:
                        try:
                            if s3_storage.delete_file(resume.content_s3_key):
                                deletion_summary["deleted"]["resume_s3_files"] += 1
                                deletion_summary["deleted"]["s3_files_deleted"].append(resume.content_s3_key)
                                logger.info(f"Deleted S3 resume content: {resume.content_s3_key}")
                            else:
                                deletion_summary["deleted"]["s3_deletion_errors"].append(f"Failed to delete resume content S3 file: {resume.content_s3_key}")
                        except Exception as e:
                            logger.error(f"Error deleting S3 resume content {resume.content_s3_key}: {str(e)}")
                            deletion_summary["deleted"]["s3_deletion_errors"].append(f"Error deleting resume content S3 file: {str(e)}")
                
                # Count profile sections before deletion (they will be cascade deleted)
                deletion_summary["deleted"]["resumes"] = len(resumes)
                deletion_summary["deleted"]["work_experiences"] = len(profile.work_experiences)
                deletion_summary["deleted"]["educations"] = len(profile.educations)
                deletion_summary["deleted"]["skills"] = len(profile.skills)
                deletion_summary["deleted"]["projects"] = len(profile.projects)
                deletion_summary["deleted"]["publications"] = len(profile.publications)
                deletion_summary["deleted"]["volunteer_works"] = len(profile.volunteer_works)
            
            # Delete the user (this will cascade delete everything due to our model relationships)
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"Successfully deleted user {user_id} and all associated data")
            return deletion_summary
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during user deletion {user_id}: {str(e)}")
            raise Exception(f"Failed to delete user: {str(e)}")
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all data associated with a user before deletion.
        Useful for showing what will be deleted.
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"error": "User not found"}
            
            summary = {
                "user_id": str(user_id),
                "user_email": user.email,
                "user_type": user.user_type,
                "credits": user.credits,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "profile": None,
                "data_counts": {
                    "resumes": 0,
                    "work_experiences": 0,
                    "educations": 0,
                    "skills": 0,
                    "projects": 0,
                    "publications": 0,
                    "volunteer_works": 0
                },
                "files": {
                    "uploaded_resume_local": None,
                    "uploaded_resume_s3": None,
                    "resume_s3_files": []
                }
            }
            
            if user.profile:
                profile = user.profile
                summary["profile"] = {
                    "name": profile.name,
                    "phone": profile.phone,
                    "country": profile.country,
                    "city": profile.city,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None
                }
                
                # Count all data
                summary["data_counts"]["resumes"] = len(profile.resumes)
                summary["data_counts"]["work_experiences"] = len(profile.work_experiences)
                summary["data_counts"]["educations"] = len(profile.educations)
                summary["data_counts"]["skills"] = len(profile.skills)
                summary["data_counts"]["projects"] = len(profile.projects)
                summary["data_counts"]["publications"] = len(profile.publications)
                summary["data_counts"]["volunteer_works"] = len(profile.volunteer_works)
                
                # File information
                if profile.resume_s3_key:
                    summary["files"]["uploaded_resume_s3"] = profile.resume_s3_key
                
                # Resume S3 files
                for resume in profile.resumes:
                    if resume.content_s3_key:
                        summary["files"]["resume_s3_files"].append({
                            "resume_id": str(resume.id),
                            "resume_name": resume.name,
                            "s3_key": resume.content_s3_key
                        })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting user data summary for {user_id}: {str(e)}")
            return {"error": f"Failed to get user data summary: {str(e)}"}

def cleanup_user_data(db: Session, user_id: str) -> Dict[str, Any]:
    """
    Convenience function to completely delete a user and all associated data.
    """
    cleanup = UserDataCleanup(db)
    return cleanup.delete_user_completely(user_id)

def get_user_deletion_preview(db: Session, user_id: str) -> Dict[str, Any]:
    """
    Convenience function to get a preview of what will be deleted for a user.
    """
    cleanup = UserDataCleanup(db)
    return cleanup.get_user_data_summary(user_id)
