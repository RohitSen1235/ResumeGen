import asyncio
import tempfile
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, status, Request
from pydantic import BaseModel
import sqlalchemy.exc
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import groq
import stripe
from .database import get_redis
from typing import Optional, Tuple, List
from uuid import UUID
import os
import time
from dotenv import load_dotenv
import logging
import json
import traceback
import re
from pathlib import Path
from datetime import timedelta
from sqlalchemy.orm import Session
from .latex.processor import LatexProcessor
from .database import *
from . import models, schemas
from .utils.auth import (
    get_password_hash,
    refresh_access_token,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_token
)
from .database import (
    save_generation_status,
    get_generation_status,
    save_generation_result,
    get_generation_result,
    cleanup_generation_cache
)
from .utils.linkedin_oauth import linkedin_oauth

from .utils.email import send_email
from .utils.resume_generator import ResumeGenerator
from .utils.resume_parser import parse_pdf_resume
from .utils.groq_parser import GroqResumeParser
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
stripe_price_id = os.getenv("STRIPE_PRICE_ID")

# Validate environment variables
REQUIRED_ENV_VARS = {
    "GROQ_API_KEY": "API key for Groq",
    "GROQ_MODEL": "Model to use for generation (e.g., mixtral-8x7b-32768)"
}

missing_vars = []
for var, description in REQUIRED_ENV_VARS.items():
    if not os.getenv(var):
        missing_vars.append(f"{var} ({description})")

if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg)
    raise ValueError(error_msg)

# Get environment variables
api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL")
isProd = os.getenv("PROD_MODE")

# Initialize Groq client
groq_client = groq.Groq(api_key=api_key)

app = FastAPI()

# Create output directory if it doesn't exist
output_dir = Path(__file__).parent / "output"
output_dir.mkdir(exist_ok=True, parents=True)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "https://resumegenie.rsfreelance.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize LaTeX processor
latex_processor = LatexProcessor()

# Authentication endpoints
@app.post("/api/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/forgot-password")
async def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Initiate password reset by sending reset token to email."""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Generate reset token (expires in 1 hour)
    reset_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(hours=1)
    )
    
    # Create reset link
    if isProd:
        host = f"https://{os.getenv('PROD_HOST')}"
        reset_link = f"{host}/reset-password?token={reset_token}"
    else:    
        reset_link = f"http://localhost/reset-password?token={reset_token}"
    
    # Send email
    email_sent = send_email(
        to_email=user.email,  # Access the string value from SQLAlchemy model # type: ignore
        subject="Password Reset Request",
        message=f"""Please click the link below to reset your password:
        
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.
"""
    )
    
    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send password reset email"
        )
    
    return {"message": "Password reset initiated. Check your email for instructions."}

@app.get("/api/reset-password")
async def verify_reset_token(token: str):
    """Verify reset token and return user email if valid."""
    try:
        email = verify_token(token)
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired token"
            )
        return {"email": email}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )

@app.post("/api/reset-password")
async def reset_password(
    request: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using valid reset token."""
    try:
        # Verify token
        email = verify_token(request.token)
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired token"
            )
            
        # Find user
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
            
        # Update password
        user.hashed_password = get_password_hash(request.new_password) # type: ignore
        db.commit()
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error resetting password"
        )

@app.post("/api/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to get access token."""
    try:
        # Log the login attempt
        logger.info(f"Login attempt for user: {form_data.username}")
        
        # Find user by email
        user = db.query(models.User).filter(models.User.email == form_data.username).first()
        if not user:
            logger.warning(f"Login failed: User not found - {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User Not Found, Please Sign Up to use the app",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(form_data.password, user.hashed_password): # type: ignore
            logger.warning(f"Login failed: Invalid password for user - {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login successful for user: {form_data.username}")
        response = JSONResponse(
            content={"access_token": access_token, "token_type": "bearer"}
        )
        response.set_cookie(
            key="auth_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        return response
        
    except HTTPException:
        raise
    except sqlalchemy.exc.OperationalError as e:
        if "relation \"users\" does not exist" in str(e):
            logger.error(f"Database schema error: Users table does not exist")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during login"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )

@app.post("/api/token/refresh", response_model=schemas.Token)
async def refresh_token(
    token: str = Form(...),
    db: Session = Depends(get_db)
):
    """Refresh an access token that is near expiration."""
    try:
        new_token = refresh_access_token(token)
        return {"access_token": new_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )

@app.get("/api/user", response_model=schemas.User)
async def get_current_user_data(current_user: models.User = Depends(get_current_user)):
    """Get current user data."""
    return current_user

@app.put("/api/user-type")
async def update_user_type(
    user_type: str = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user type (student, job_seeker, career_changer, other)"""
    if user_type not in ["student", "job_seeker", "career_changer", "other"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid user type"
        )
    
    current_user.user_type = user_type
    db.commit()
    db.refresh(current_user)
    return {"message": "User type updated successfully"}

# LinkedIn OAuth endpoints
@app.get("/api/auth/linkedin")
async def linkedin_login():
    """Initiate LinkedIn OAuth login"""
    import secrets
    state = secrets.token_urlsafe(32)
    
    # Store state in session/cache for verification (simplified for demo)
    # In production, you'd want to store this in Redis with expiration
    
    auth_url = linkedin_oauth.get_authorization_url(state)
    return {"auth_url": auth_url, "state": state}

@app.get("/api/auth/linkedin/callback")
async def linkedin_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle LinkedIn OAuth callback"""
    try:
        # Exchange code for access token
        token_data = await linkedin_oauth.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Get user profile from LinkedIn and validate with schema
        linkedin_profile = await linkedin_oauth.get_user_profile(access_token)
        validated_profile = schemas.LinkedInProfile(**linkedin_profile)
        
        if not validated_profile.email:
            raise HTTPException(status_code=400, detail="Email not provided by LinkedIn")
        
        # Check if user already exists
        user = db.query(models.User).filter(models.User.email == validated_profile.email).first()
        
        if user:
            # Update OAuth info if user exists
            user.oauth_provider = "linkedin"
            user.oauth_id = validated_profile.id
        else:
            # Create new user
            user = models.User(
                email=validated_profile.email,
                oauth_provider="linkedin",
                oauth_id=validated_profile.id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create or update profile with LinkedIn data
        profile_data = {
            "name": f"{validated_profile.first_name} {validated_profile.last_name}",
            "linkedin_url": f"https://www.linkedin.com/in/{validated_profile.id}",
            "professional_info": validated_profile.dict(exclude_unset=True)
        }
        
        if not user.profile:
            db_profile = models.Profile(**profile_data, user_id=user.id)
            db.add(db_profile)
        else:
            # Update existing profile with LinkedIn data
            for key, value in profile_data.items():
                setattr(user.profile, key, value)
        
        db.commit()
        db.refresh(user)
        
        # Create JWT token for the user
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        response = JSONResponse(
            content={
                "access_token": jwt_token,
                "token_type": "bearer",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "profile": {
                        "name": user.profile.name if user.profile else "",
                        "linkedin_url": user.profile.linkedin_url if user.profile else ""
                    }
                }
            }
        )
        response.set_cookie(
            key="auth_token",
            value=jwt_token,
            httponly=True,
            secure=True,
            samesite="None",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LinkedIn OAuth callback error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="LinkedIn authentication failed"
        )

# Profile endpoints
@app.post("/api/profile", response_model=schemas.Profile)
async def create_profile(
    profile: schemas.ProfileCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create user profile."""
    if current_user.profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )
    
    db_profile = models.Profile(**profile.dict(), user_id=current_user.id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/api/profile", response_model=schemas.Profile)
async def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile."""
    if not current_user.profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    return current_user.profile

@app.put("/api/profile", response_model=schemas.Profile)
async def update_profile(
    profile: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    if not current_user.profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    update_data = profile.dict(exclude_unset=True)
    
    if "onboarding_completed" in update_data:
        current_user.onboarding_completed = update_data.pop("onboarding_completed")

    for key, value in update_data.items():
        setattr(current_user.profile, key, value)
    
    db.commit()
    db.refresh(current_user.profile)
    return current_user.profile

@app.post("/api/upload-resume")
async def upload_resume(
    resume: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process a resume file."""
    try:
        if not current_user.profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found. Please create a profile first."
            )

        # Read the file content into memory
        content = await resume.read()

        # Parse resume to extract text and populate profile sections
        parsed_resume_for_response = None
        parsed_data = None  # Initialize parsed_data at the top level
        try:
            # Step 1: Extract raw text from PDF for Groq parsing
            from .utils.resume_parser import extract_text_with_fitz
            
            resume_text = str

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
                tmp.write(content)
                tmp.flush()  # Ensure all data is written to disk
                resume_text = extract_text_with_fitz(tmp.name)
            
            if resume_text and not resume_text.startswith("An error occurred"):
                logger.info("Parsing resume with Groq to populate profile sections...")
                logger.info(f"Resume text length: {len(resume_text)} characters")
                
                # Step 2: Use Groq parser to get structured data
                groq_parser = GroqResumeParser()
                structured_data = groq_parser.parse_resume(resume_text)

                if not structured_data:
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to parse resume. Please try again with a different file."
                    )

                parsed_resume_for_response = structured_data.dict()
                
                logger.info(f"Groq parsing completed. Found {len(structured_data.work_experience)} work experiences, {len(structured_data.education)} education entries, {len(structured_data.skills)} skills, {len(structured_data.projects)} projects")
                
                # Step 3: Also run the old parser for backward compatibility
                parsed_data = parse_pdf_resume(content)
                if isinstance(parsed_data, dict) and "error" not in parsed_data:
                    current_user.profile.professional_info = parsed_data
                
                # Step 4: Populate profile sections with structured data
                profile = current_user.profile
                
                # Update profile basic info
                if structured_data.summary:
                    profile.summary = structured_data.summary
                if structured_data.professional_title:
                    profile.professional_title = structured_data.professional_title
                
                # Clear existing sections
                db.query(models.WorkExperience).filter(models.WorkExperience.profile_id == profile.id).delete()
                db.query(models.Education).filter(models.Education.profile_id == profile.id).delete()
                db.query(models.Skill).filter(models.Skill.profile_id == profile.id).delete()
                db.query(models.Project).filter(models.Project.profile_id == profile.id).delete()
                db.query(models.Publication).filter(models.Publication.profile_id == profile.id).delete()
                db.query(models.VolunteerWork).filter(models.VolunteerWork.profile_id == profile.id).delete()
                
                # Import work experience
                for exp in structured_data.work_experience:
                    db_exp = models.WorkExperience(
                        profile_id=profile.id,
                        position=exp.position,
                        company=exp.company,
                        country=exp.country,
                        city=exp.city,
                        start_date=exp.start_date,
                        end_date=exp.end_date,
                        current_job=exp.current_job,
                        description=exp.description,
                        achievements=exp.achievements,
                        technologies=exp.technologies
                    )
                    db.add(db_exp)
                
                # Import education
                for edu in structured_data.education:
                    db_edu = models.Education(
                        profile_id=profile.id,
                        institution=edu.institution,
                        degree=edu.degree,
                        field_of_study=edu.field_of_study,
                        country=edu.country,
                        city=edu.city,
                        start_date=edu.start_date,
                        end_date=edu.end_date,
                        gpa=edu.gpa,
                        description=edu.description,
                        achievements=edu.achievements
                    )
                    db.add(db_edu)
                
                # Import skills
                for skill in structured_data.skills:
                    db_skill = models.Skill(
                        profile_id=profile.id,
                        name=skill.name,
                        category=skill.category,
                        proficiency=skill.proficiency,
                        years_experience=skill.years_experience
                    )
                    db.add(db_skill)
                
                # Import projects
                for project in structured_data.projects:
                    db_project = models.Project(
                        profile_id=profile.id,
                        name=project.name,
                        description=project.description,
                        url=project.url,
                        industry=project.industry,
                        start_date=project.start_date,
                        end_date=project.end_date,
                        technologies=project.technologies,
                        achievements=project.achievements
                    )
                    db.add(db_project)
                
                # Import publications
                for pub in structured_data.publications:
                    db_pub = models.Publication(
                        profile_id=profile.id,
                        title=pub.title,
                        publisher=pub.publisher,
                        publication_date=pub.publication_date,
                        url=pub.url,
                        description=pub.description,
                        authors=pub.authors
                    )
                    db.add(db_pub)
                
                # Import volunteer work
                for vol in structured_data.volunteer_work:
                    db_vol = models.VolunteerWork(
                        profile_id=profile.id,
                        organization=vol.organization,
                        role=vol.role,
                        cause=vol.cause,
                        country=vol.country,
                        city=vol.city,
                        start_date=vol.start_date,
                        end_date=vol.end_date,
                        current_role=vol.current_role,
                        description=vol.description,
                        achievements=vol.achievements
                    )
                    db.add(db_vol)
                
                logger.info("Successfully populated profile sections from resume")
            else:
                logger.warning("Failed to extract text from resume or text was empty")
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            # Continue even if parsing fails

        db.commit()
        return {
            "message": "Resume uploaded and profile sections populated successfully",
            "parsed_data": parsed_resume_for_response
        }

    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading resume: {str(e)}"
        )

# Admin endpoints
@app.get("/api/admin/users", response_model=List[schemas.User])
async def admin_get_users(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(models.User).all()
    return users

@app.post("/api/admin/users", response_model=schemas.User)
async def admin_create_user(
    user: schemas.UserCreateAdmin,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/api/admin/users/{user_id}", response_model=schemas.User)
async def admin_update_user(
    user_id: UUID,
    user_update: schemas.UserUpdateAdmin,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user (admin only)"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user_update.email:
        db_user.email = user_update.email
    if user_update.is_admin is not None:
        db_user.is_admin = user_update.is_admin
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/admin/users/{user_id}/data-preview")
async def admin_get_user_data_preview(
    user_id: UUID,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a preview of all data associated with a user before deletion (admin only)"""
    try:
        from .utils.user_cleanup import get_user_deletion_preview
        
        preview = get_user_deletion_preview(db, str(user_id))
        
        if "error" in preview:
            raise HTTPException(
                status_code=404,
                detail=preview["error"]
            )
        
        return preview
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user data preview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting user data preview: {str(e)}"
        )

@app.delete("/api/admin/users/{user_id}")
async def admin_delete_user(
    user_id: UUID,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user and all associated data including S3 files (admin only)"""
    try:
        from .utils.user_cleanup import cleanup_user_data
        
        # Perform complete user data cleanup
        deletion_result = cleanup_user_data(db, str(user_id))
        
        if "error" in deletion_result:
            raise HTTPException(
                status_code=404,
                detail=deletion_result["error"]
            )
        
        logger.info(f"Admin {current_admin.email} deleted user {user_id}")
        logger.info(f"Deletion summary: {deletion_result}")
        
        return {
            "message": "User and all associated data deleted successfully",
            "deletion_summary": deletion_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin user deletion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting user: {str(e)}"
        )

@app.post("/api/admin/users/credits")
async def admin_update_user_credits(
    credit_update: schemas.UserCreditUpdate,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user credits (admin only)"""
    db_user = db.query(models.User).filter(models.User.id == credit_update.user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if credit_update.operation == "add":
        db_user.credits += credit_update.credits
    else:  # set
        db_user.credits = credit_update.credits
    
    db.commit()
    db.refresh(db_user)
    return {"message": "Credits updated successfully", "credits": db_user.credits}

@app.get("/api/admin/templates")
async def admin_get_templates(
    current_admin: models.User = Depends(get_current_admin_user)
):
    """Get all templates (admin only)"""
    try:
        latex_processor = LatexProcessor()
        templates = latex_processor.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting templates: {str(e)}"
        )

@app.post("/api/admin/templates")
async def admin_add_template(
    template_data: dict,
    current_admin: models.User = Depends(get_current_admin_user)
):
    """Add new template (admin only)"""
    try:
        latex_processor = LatexProcessor()
        result = latex_processor.add_template(template_data)
        return {"message": "Template added successfully", "template": result}
    except Exception as e:
        logger.error(f"Error adding template: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding template: {str(e)}"
        )

@app.get("/api/admin/analytics")
async def admin_get_analytics(
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get usage analytics (admin only)"""
    try:
        # Get total users
        total_users = db.query(models.User).count()
        
        # Get active users (used in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users = db.query(models.User)\
            .join(models.Profile)\
            .join(models.Resume)\
            .filter(models.Resume.created_at >= thirty_days_ago)\
            .distinct()\
            .count()
            
        # Get resume generation stats
        total_resumes = db.query(models.Resume).count()
        resumes_last_30_days = db.query(models.Resume)\
            .filter(models.Resume.created_at >= thirty_days_ago)\
            .count()
            
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_resumes": total_resumes,
            "resumes_last_30_days": resumes_last_30_days
        }
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting analytics: {str(e)}"
        )

# Resume generation endpoints
from typing import List, Optional

@app.get("/api/templates")
async def get_templates():
    """Get list of available resume templates"""
    try:
        latex_processor = LatexProcessor()
        templates = latex_processor.get_available_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting templates: {str(e)}"
        )


@app.post("/api/generate-pdf")
async def generate_pdf_endpoint(
    resume_data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF from optimized resume data."""
    if not current_user.profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete your profile first"
        )
    
    # Extract template_id from resume_data if provided
    template_id = resume_data.get('template_id')
    
    profile = current_user.profile
    personal_info = {
        "name": profile.name,
        "email": current_user.email,
        "phone": profile.phone,
        "location": ", ".join(filter(None, [profile.city, profile.country])),
        "linkedin": profile.linkedin_url
    }
    
    resume_generator = ResumeGenerator()
    try:
        logger.info(f"Creating Resume using Template : {template_id} ")
        result = await resume_generator.generate_resume(
            resume_data=resume_data,
            personal_info=personal_info,
            job_title=resume_data.get('job_title', 'Resume'),
            format='pdf',
            template_id=template_id
        )
        
        # Handle both tuple (path, usage) and dict return formats
        if isinstance(result, tuple):
            pdf_path, _ = result
        else:
            pdf_path = result['pdf_path']
        
        if not pdf_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF resume"
            )
        
        pdf_url = f"/download-resume/{os.path.basename(pdf_path)}"
        return {"pdf_url": pdf_url}
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )

@app.post("/api/generate-resume-docx")
async def generate_resume_docx_endpoint(
    resume_data: dict,
    current_user: models.User = Depends(get_current_user)
):
    """Generate DOCX version of resume on demand"""
    try:
        logger.info("Starting DOCX resume generation")
        logger.info(f"Received resume data keys: {resume_data.keys()}")
        
        # Get user profile
        if not current_user.profile:
            raise HTTPException(
                status_code=400,
                detail="Please complete your profile first"
            )
        
        profile = current_user.profile
        personal_info = {
            "name": profile.name,
            "email": current_user.email,
            "phone": profile.phone,
            "location": ", ".join(filter(None, [profile.city, profile.country])),
            "linkedin": profile.linkedin_url
        }
        logger.info(f"Personal info prepared: {personal_info}")
        
        # Validate required fields
        if 'ai_content' not in resume_data:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: ai_content"
            )
        
        # Generate DOCX using LaTeX processor
        resume_generator = ResumeGenerator()
        docx_path, _ = await resume_generator.generate_resume(
            resume_data={
                'ai_content': resume_data['ai_content']
            },
            personal_info=personal_info,
            job_title=resume_data.get('job_title', 'Resume'),
            format='docx'
        )
        
        if not docx_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate DOCX resume"
            )
        
        docx_url = f"/download-resume/{os.path.basename(docx_path)}"
        logger.info(f"Successfully generated DOCX at: {docx_path}")
        return {"docx_url": docx_url}
        
    except Exception as e:
        logger.error(f"Error generating DOCX resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating DOCX resume: {str(e)}"
        )

@app.post("/api/generate-resume-test")
async def generate_resume_test(
    resume_data: dict
):
    """Test endpoint to generate resume from direct JSON input."""
    try:
        # Validate required fields
        required_fields = ["name", "email", "job_title", "summary", "skills", "experience", "education"]
        for field in required_fields:
            if field not in resume_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )

        # Generate PDF using LaTeX processor
        latex_processor = LatexProcessor()
        pdf_path = latex_processor.generate_resume_pdf(resume_data)
        
        if not pdf_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF resume"
            )
        
        return {
            "pdf_path": pdf_path,
            "message": "Resume generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_resume_test: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/download-resume/{filename}")
async def download_resume(
    filename: str,
    current_user: models.User = Depends(get_current_user)
):
    """Download generated PDF resume."""
    try:
        pdf_path = Path(__file__).parent / "output" / filename
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Resume PDF not found")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading resume")

@app.post("/api/generate-report")
async def generate_report_endpoint(
    resume_data: dict,
    current_user: models.User = Depends(get_current_user)
):
    """Generate a PDF report from resume generation data."""
    try:
        # Initialize resume generator
        resume_generator = ResumeGenerator()
        
        # Generate the report PDF
        report_pdf_path = await resume_generator.generate_report_pdf(
            resume_data['agent_outputs'],
            resume_data['total_usage']
        )
        
        # Return the report download URL
        report_url = f"/api/download-report/{os.path.basename(report_pdf_path)}"
        return {"report_url": report_url}
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )

@app.get("/api/download-report/{filename}")
async def download_report(
    filename: str,
    current_user: models.User = Depends(get_current_user)
):
    """Download generated PDF report."""
    try:
        pdf_path = Path(__file__).parent / "output" / filename
        if not pdf_path.exists():
            raise HTTPException(status_code=404, detail="Report PDF not found")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading report")

async def read_job_description(job_description: UploadFile) -> str:
    """Read and decode the job description file content."""
    try:
        content = await job_description.read()
        
        # Try different encodings
        try:
            job_desc_text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                job_desc_text = content.decode("latin-1")
            except:
                job_desc_text = content.decode("utf-8", errors="ignore")
        
        if len(job_desc_text.strip()) == 0:
            raise ValueError("Job description file is empty")
            
        return job_desc_text
        
    except Exception as e:
        logger.error(f"Error reading job description file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error reading job description file: {str(e)}"
        )

def extract_job_title(text: str) -> str:
    """Extract job title from job description using Groq."""
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a an expert recruiter. Extract only the main job title/role from the given job description. Return only the title, nothing else."},
                {"role": "user", "content": f"Extract the main job title from this job description:\n\n{text}"}
            ],
            model=model_name, # type: ignore
            temperature=0.7,
            max_tokens=30
        )
        job_title = completion.choices[0].message.content.strip() # type: ignore
        # Clean up the job title
        job_title = re.sub(r'[^\w\s-]', '', job_title)
        job_title = job_title.replace(' ', '-').lower()
        return job_title
    except Exception as e:
        logger.error(f"Error extracting job title: {str(e)}")
        return "Ambiguous_job_title"

@app.get("/api/resumes")
async def get_resumes(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's resume history"""
    if not current_user.profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    resumes = db.query(models.Resume)\
        .filter(models.Resume.profile_id == current_user.profile.id)\
        .order_by(models.Resume.created_at.desc())\
        .all()
    
    return [
        {
            "id": str(resume.id),
            "name": resume.name,
            "version": resume.version,
            "created_at": resume.created_at.isoformat(),
            "status": resume.status
        }
        for resume in resumes
    ]

from uuid import UUID

@app.get("/api/resume/{resume_id}")
async def get_resume(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID"""
    resume = db.query(models.Resume)\
        .filter(models.Resume.id == resume_id)\
        .first()
    
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )
    
    # Get content from S3 if available, otherwise use DB content
    content = resume.content  # Default to DB content
    if resume.content_s3_key:
        try:
            from .utils.s3_storage import s3_storage
            s3_content = s3_storage.download_text(resume.content_s3_key)
            if s3_content:
                content = s3_content
                logger.info(f"Retrieved resume content from S3 for resume {resume_id}")
            else:
                logger.warning(f"Failed to retrieve content from S3 for resume {resume_id}, using DB content")
        except Exception as e:
            logger.error(f"Error retrieving content from S3 for resume {resume_id}: {str(e)}")
            # Fall back to DB content
    
    return {
        "id": str(resume.id),
        "name": resume.name,
        "version": resume.version,
        "content": content,
        "job_description": resume.job_description,
        "status": resume.status,
        "created_at": resume.created_at.isoformat(),
        "updated_at": resume.updated_at.isoformat() if resume.updated_at else None # type: ignore
    }

@app.put("/api/resume/{resume_id}")
async def update_resume_content(
    resume_id: UUID,
    content_update: schemas.ResumeContentUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update resume content"""
    try:
        resume = db.query(models.Resume)\
            .filter(models.Resume.id == resume_id)\
            .filter(models.Resume.profile_id == current_user.profile.id)\
            .first()
        
        if not resume:
            raise HTTPException(
                status_code=404,
                detail="Resume not found"
            )
        
        # Try to update content in S3 first
        s3_update_success = False
        if resume.content_s3_key:
            try:
                from .utils.s3_storage import s3_storage
                s3_update_success = s3_storage.upload_text(content_update.content, resume.content_s3_key)
                if s3_update_success:
                    logger.info(f"Successfully updated resume content in S3 for resume {resume_id}")
                else:
                    logger.error(f"Failed to update resume content in S3 for resume {resume_id}")
            except Exception as s3_error:
                logger.error(f"Error updating content in S3 for resume {resume_id}: {str(s3_error)}")
        
        # Update database content based on S3 success
        if s3_update_success:
            # S3 update successful - clear DB content (S3 is primary storage)
            resume.content = None
            logger.info(f"S3 update successful, cleared DB content for resume {resume_id}")
        else:
            # S3 update failed or no S3 key - store content in DB as fallback
            resume.content = content_update.content
            logger.warning(f"S3 update failed, storing content in DB as fallback for resume {resume_id}")
        
        resume.updated_at = datetime.now()
        
        db.commit()
        db.refresh(resume)
        
        return {
            "message": "Resume content updated successfully",
            "content": resume.content
        }
    except Exception as e:
        logger.error(f"Error updating resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating resume: {str(e)}"
        )

@app.delete("/api/resumes/{resume_id}")
async def delete_resume_by_id(
    resume_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific resume by ID"""
    if not current_user.profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found"
        )
    
    resume = db.query(models.Resume)\
        .filter(models.Resume.id == resume_id)\
        .filter(models.Resume.profile_id == current_user.profile.id)\
        .first()
    
    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )
    
    # Delete from S3 if S3 key exists
    if resume.content_s3_key:
        try:
            from .utils.s3_storage import s3_storage
            s3_delete_success = s3_storage.delete_file(resume.content_s3_key)
            if s3_delete_success:
                logger.info(f"Successfully deleted resume content from S3 for resume {resume_id}")
            else:
                logger.warning(f"Failed to delete resume content from S3 for resume {resume_id}")
        except Exception as s3_error:
            logger.error(f"Error deleting content from S3 for resume {resume_id}: {str(s3_error)}")
            # Continue with DB deletion even if S3 deletion fails
    
    # Delete from database
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}

@app.delete("/resumes/{resume_id}")
async def delete_resume_legacy(
    resume_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Legacy endpoint for deleting resumes (maintained for backward compatibility)"""
    return await delete_resume_by_id(resume_id, current_user, db)


# Resume parsing endpoint
@app.post("/api/parse-resume", response_model=schemas.ResumeParseResponse)
async def parse_resume_with_groq(
    request: schemas.ResumeParseRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Parse resume text using Groq AI and return structured data"""
    try:
        parser = GroqResumeParser()
        parsed_data = parser.parse_resume(request.resume_text)
        return parsed_data
    except Exception as e:
        logger.error(f"Error parsing resume with Groq: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing resume: {str(e)}"
        )

@app.post("/api/import-resume-sections")
async def import_resume_sections(
    parsed_data: schemas.ResumeParseResponse,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import parsed resume data into profile sections"""
    try:
        if not current_user.profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )
        
        profile = current_user.profile
        
        # Update profile basic info
        if parsed_data.summary:
            profile.summary = parsed_data.summary
        if parsed_data.professional_title:
            profile.professional_title = parsed_data.professional_title
        
        # Clear existing sections
        db.query(models.WorkExperience).filter(models.WorkExperience.profile_id == profile.id).delete()
        db.query(models.Education).filter(models.Education.profile_id == profile.id).delete()
        db.query(models.Skill).filter(models.Skill.profile_id == profile.id).delete()
        db.query(models.Project).filter(models.Project.profile_id == profile.id).delete()
        db.query(models.Publication).filter(models.Publication.profile_id == profile.id).delete()
        db.query(models.VolunteerWork).filter(models.VolunteerWork.profile_id == profile.id).delete()
        
        # Import work experience
        for exp in parsed_data.work_experience:
            db_exp = models.WorkExperience(
                profile_id=profile.id,
                position=exp.position,
                company=exp.company,
                country=exp.country,
                city=exp.city,
                start_date=exp.start_date,
                end_date=exp.end_date,
                current_job=exp.current_job,
                description=exp.description,
                achievements=exp.achievements,
                technologies=exp.technologies
            )
            db.add(db_exp)
        
        # Import education
        for edu in parsed_data.education:
            db_edu = models.Education(
                profile_id=profile.id,
                institution=edu.institution,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                country=edu.country,
                city=edu.city,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=edu.gpa,
                description=edu.description,
                achievements=edu.achievements
            )
            db.add(db_edu)
        
        # Import skills
        for skill in parsed_data.skills:
            db_skill = models.Skill(
                profile_id=profile.id,
                name=skill.name,
                category=skill.category,
                proficiency=skill.proficiency,
                years_experience=skill.years_experience
            )
            db.add(db_skill)
        
        # Import projects
        for project in parsed_data.projects:
            db_project = models.Project(
                profile_id=profile.id,
                name=project.name,
                description=project.description,
                url=project.url,
                industry=project.industry,
                start_date=project.start_date,
                end_date=project.end_date,
                technologies=project.technologies,
                achievements=project.achievements
            )
            db.add(db_project)
        
        # Import publications
        for pub in parsed_data.publications:
            db_pub = models.Publication(
                profile_id=profile.id,
                title=pub.title,
                publisher=pub.publisher,
                publication_date=pub.publication_date,
                url=pub.url,
                description=pub.description,
                authors=pub.authors
            )
            db.add(db_pub)
        
        # Import volunteer work
        for vol in parsed_data.volunteer_work:
            db_vol = models.VolunteerWork(
                profile_id=profile.id,
                organization=vol.organization,
                role=vol.role,
                cause=vol.cause,
                country=vol.country,
                city=vol.city,
                start_date=vol.start_date,
                end_date=vol.end_date,
                current_role=vol.current_role,
                description=vol.description,
                achievements=vol.achievements
            )
            db.add(db_vol)
        
        db.commit()
        return {"message": "Resume sections imported successfully"}
        
    except Exception as e:
        logger.error(f"Error importing resume sections: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error importing resume sections: {str(e)}"
        )

# Work Experience endpoints
@app.get("/api/profile/work-experience", response_model=List[schemas.WorkExperience])
async def get_work_experience(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's work experience"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    experiences = db.query(models.WorkExperience)\
        .filter(models.WorkExperience.profile_id == current_user.profile.id)\
        .order_by(models.WorkExperience.start_date.desc())\
        .all()
    return experiences

@app.post("/api/profile/work-experience", response_model=schemas.WorkExperience)
async def create_work_experience(
    experience: schemas.WorkExperienceCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new work experience"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_exp = models.WorkExperience(**experience.dict(), profile_id=current_user.profile.id)
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@app.put("/api/profile/work-experience/{exp_id}", response_model=schemas.WorkExperience)
async def update_work_experience(
    exp_id: UUID,
    experience: schemas.WorkExperienceUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update work experience"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_exp = db.query(models.WorkExperience)\
        .filter(models.WorkExperience.id == exp_id)\
        .filter(models.WorkExperience.profile_id == current_user.profile.id)\
        .first()
    
    if not db_exp:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    for key, value in experience.dict(exclude_unset=True).items():
        setattr(db_exp, key, value)
    
    db.commit()
    db.refresh(db_exp)
    return db_exp

@app.delete("/api/profile/work-experience/{exp_id}")
async def delete_work_experience(
    exp_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete work experience"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_exp = db.query(models.WorkExperience)\
        .filter(models.WorkExperience.id == exp_id)\
        .filter(models.WorkExperience.profile_id == current_user.profile.id)\
        .first()
    
    if not db_exp:
        raise HTTPException(status_code=404, detail="Work experience not found")
    
    db.delete(db_exp)
    db.commit()
    return {"message": "Work experience deleted successfully"}

# Education endpoints
@app.get("/api/profile/education", response_model=List[schemas.EducationSection])
async def get_education(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's education"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    education = db.query(models.Education)\
        .filter(models.Education.profile_id == current_user.profile.id)\
        .order_by(models.Education.start_date.desc())\
        .all()
    return education

@app.post("/api/profile/education", response_model=schemas.EducationSection)
async def create_education(
    education: schemas.EducationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new education"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_edu = models.Education(**education.dict(), profile_id=current_user.profile.id)
    db.add(db_edu)
    db.commit()
    db.refresh(db_edu)
    return db_edu

@app.put("/api/profile/education/{edu_id}", response_model=schemas.EducationSection)
async def update_education(
    edu_id: UUID,
    education: schemas.EducationUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update education"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_edu = db.query(models.Education)\
        .filter(models.Education.id == edu_id)\
        .filter(models.Education.profile_id == current_user.profile.id)\
        .first()
    
    if not db_edu:
        raise HTTPException(status_code=404, detail="Education not found")
    
    for key, value in education.dict(exclude_unset=True).items():
        setattr(db_edu, key, value)
    
    db.commit()
    db.refresh(db_edu)
    return db_edu

@app.delete("/api/profile/education/{edu_id}")
async def delete_education(
    edu_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete education"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_edu = db.query(models.Education)\
        .filter(models.Education.id == edu_id)\
        .filter(models.Education.profile_id == current_user.profile.id)\
        .first()
    
    if not db_edu:
        raise HTTPException(status_code=404, detail="Education not found")
    
    db.delete(db_edu)
    db.commit()
    return {"message": "Education deleted successfully"}

# Skills endpoints
@app.get("/api/profile/skills", response_model=List[schemas.SkillSection])
async def get_skills(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's skills"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    skills = db.query(models.Skill)\
        .filter(models.Skill.profile_id == current_user.profile.id)\
        .order_by(models.Skill.category, models.Skill.name)\
        .all()
    return skills

@app.post("/api/profile/skills", response_model=schemas.SkillSection)
async def create_skill(
    skill: schemas.SkillCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new skill"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_skill = models.Skill(**skill.dict(), profile_id=current_user.profile.id)
    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)
    return db_skill

@app.put("/api/profile/skills/{skill_id}", response_model=schemas.SkillSection)
async def update_skill(
    skill_id: UUID,
    skill: schemas.SkillUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update skill"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_skill = db.query(models.Skill)\
        .filter(models.Skill.id == skill_id)\
        .filter(models.Skill.profile_id == current_user.profile.id)\
        .first()
    
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    for key, value in skill.dict(exclude_unset=True).items():
        setattr(db_skill, key, value)
    
    db.commit()
    db.refresh(db_skill)
    return db_skill

@app.delete("/api/profile/skills/{skill_id}")
async def delete_skill(
    skill_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete skill"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_skill = db.query(models.Skill)\
        .filter(models.Skill.id == skill_id)\
        .filter(models.Skill.profile_id == current_user.profile.id)\
        .first()
    
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    db.delete(db_skill)
    db.commit()
    return {"message": "Skill deleted successfully"}

# Projects endpoints
@app.get("/api/profile/projects", response_model=List[schemas.Project])
async def get_projects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's projects"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    projects = db.query(models.Project)\
        .filter(models.Project.profile_id == current_user.profile.id)\
        .order_by(models.Project.start_date.desc())\
        .all()
    return projects

@app.post("/api/profile/projects", response_model=schemas.Project)
async def create_project(
    project: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new project"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_project = models.Project(**project.dict(), profile_id=current_user.profile.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/profile/projects/{project_id}", response_model=schemas.Project)
async def update_project(
    project_id: UUID,
    project: schemas.ProjectUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_project = db.query(models.Project)\
        .filter(models.Project.id == project_id)\
        .filter(models.Project.profile_id == current_user.profile.id)\
        .first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.dict(exclude_unset=True).items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/profile/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete project"""
    if not current_user.profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_project = db.query(models.Project)\
        .filter(models.Project.id == project_id)\
        .filter(models.Project.profile_id == current_user.profile.id)\
        .first()
    
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

# Resume generation status endpoints
@app.get("/api/generation-status/{job_id}")
async def get_generation_status_endpoint(
    job_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Get the current status of a resume generation job."""
    try:
        status_data = get_generation_status(job_id)
        if not status_data:
            raise HTTPException(
                status_code=404,
                detail="Generation job not found or expired"
            )
        return status_data
    except Exception as e:
        logger.error(f"Error getting generation status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting generation status: {str(e)}"
        )

@app.get("/api/generation-result/{job_id}")
async def get_generation_result_endpoint(
    job_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Get the result of a completed resume generation job."""
    try:
        result_data = get_generation_result(job_id)
        if not result_data:
            # Check if job is still in progress
            status_data = get_generation_status(job_id)
            if status_data and status_data['status'] != 'completed':
                raise HTTPException(
                    status_code=202,
                    detail="Generation still in progress"
                )
            raise HTTPException(
                status_code=404,
                detail="Generation result not found or expired"
            )
        return result_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting generation result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting generation result: {str(e)}"
        )

@app.post("/api/start-generation")
async def start_generation_endpoint(
    job_description: UploadFile = File(...),
    skills: Optional[List[str]] = None,
    template_id: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a resume generation job and return job ID for status polling."""
    try:
        # Get user profile
        if not current_user.profile:
            raise HTTPException(
                status_code=400,
                detail="Please complete your profile before generating a resume"
            )
        
        # Generate job ID
        job_id = generate_uuid()
        
        # Read job description
        job_desc_text = await read_job_description(job_description)
        
        # Extract job title and save to cache
        job_title = extract_job_title(job_desc_text)
        save_job_title_to_cache(job_id, job_title, expiration=1800)
        
        # Build parsed_data from profile sections
        profile = current_user.profile
        parsed_data = {
            "professional_summary": profile.summary or "Not specified",
            "past_experiences": [
                {
                    "position": exp.position,
                    "company": exp.company,
                    "start_date": exp.start_date.isoformat() if exp.start_date else None,
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "description": exp.description,
                }
                for exp in profile.work_experiences
            ],
            "skills": [skill.name for skill in profile.skills],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "start_date": edu.start_date.isoformat() if edu.start_date else None,
                    "end_date": edu.end_date.isoformat() if edu.end_date else None,
                }
                for edu in profile.educations
            ],
            "certifications": [] # Assuming no certifications are stored in the profile
        }
        
        # Start background task for generation using thread pool
        import concurrent.futures
        import threading
        
        def generate_resume_background():
            try:
                # Check credits before starting generation
                db = next(get_db())
                try:
                    user = db.query(models.User).filter(models.User.id == current_user.id).first()
                    if not user or (user.credits or 0) < 1:
                        save_generation_status(job_id, "failed", 0, "Insufficient credits", 0)
                        return
                finally:
                    db.close()
                
                # Set initial status
                save_generation_status(job_id, "parsing", 5, "Starting resume generation...")
                
                resume_generator = ResumeGenerator()
                # Use asyncio.run to handle the async function in the thread
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    optimized_data = loop.run_until_complete(
                        resume_generator.optimize_resume(
                            job_id, parsed_data, job_desc_text, skills, current_user.id
                        )
                    )
                finally:
                    loop.close()
                
                # Deduct 1 credit after successful generation
                db = next(get_db())
                try:
                    user = db.query(models.User).filter(models.User.id == current_user.id).first()
                    if user:
                        user.credits = (user.credits or 0) - 1
                        db.commit()
                        db.refresh(user)
                        logger.info(f"Deducted 1 credit from user {current_user.id}. Remaining credits: {user.credits}")
                finally:
                    db.close()
                
                # The result is already saved in optimize_resume method
                # Just log success here
                logger.info(f"Resume generation completed successfully for job {job_id}")
                
            except Exception as e:
                logger.error(f"Background generation failed for job {job_id}: {str(e)}")
                save_generation_status(job_id, "failed", 0, f"Generation failed: {str(e)}", 0)
        
        # Start the background task in a separate thread
        thread = threading.Thread(target=generate_resume_background)
        thread.daemon = True
        thread.start()
        
        return {
            "job_id": job_id,
            "message": "Resume generation started",
            "status_url": f"/api/generation-status/{job_id}",
            "result_url": f"/api/generation-result/{job_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting generation: {str(e)}"
        )




# Stripe Payment endpoints
@app.get("/api/payment/product-details")
async def get_product_details():
    """Get product details from Stripe"""
    try:
        price = stripe.Price.retrieve(os.getenv("STRIPE_PRICE_ID"))
        product = stripe.Product.retrieve(price.product)
        return {
            "amount": price.unit_amount,
            "currency": price.currency,
            "product_name": product.name,
            "credits": product.metadata.get("credits", 10)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/create-intent")
async def create_payment_intent(
    request: dict,
    current_user: models.User = Depends(get_current_user)
):
    """Create a Stripe PaymentIntent for purchasing credits"""
    try:
        # Get amount from request or use default
        amount = request.get("amount", 90000)  # Default 900 INR
        
        # Get user profile for customer information
        profile = current_user.profile
        customer_name = profile.name if profile and profile.name else current_user.email
        
        # Create or retrieve Stripe customer
        try:
            # Try to find existing customer
            customers = stripe.Customer.list(email=current_user.email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                # Create new customer
                customer = stripe.Customer.create(
                    email=current_user.email,
                    name=customer_name,
                    metadata={
                        "user_id": str(current_user.id),
                        "country": "IN"
                    }
                )
        except Exception as customer_error:
            logger.warning(f"Could not create/retrieve customer: {str(customer_error)}")
            customer = None
        
        # Create PaymentIntent with complete information
        intent_data = {
            "amount": amount,
            "currency": "inr",
            "description": "Resume-Genie.ai Credits Purchase - 10 Credits Package for AI Resume Generation",
            "metadata": {
                "user_id": str(current_user.id),
                "credits": "10",
                "price_id": stripe_price_id,
                "country": "IN",
                "product_name": "Resume-Genie.ai Credits",
                "service_type": "digital_service"
            },
            "payment_method_types": ["card"],
            "statement_descriptor": "RESUME-GENIE.AI",
            "statement_descriptor_suffix": "CREDITS"
        }
        
        # Add customer if created successfully
        if customer:
            intent_data["customer"] = customer.id
        
        intent = stripe.PaymentIntent.create(**intent_data)
        
        return {"clientSecret": intent.client_secret}
    except Exception as e:
        logger.error(f"Stripe payment intent creation failed: {str(e)}")
        # Return a more user-friendly error message
        if "indian regulations" in str(e).lower() or "registered indian business" in str(e).lower():
            raise HTTPException(
                status_code=400, 
                detail="Payment processing is currently unavailable. Please contact support for assistance with purchasing credits."
            )
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle payment success
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object
        user_id = payment_intent.metadata.get("user_id")
        credits = int(payment_intent.metadata.get("credits", 0))
        
        if user_id and credits > 0:
            # Add credits to user's account
            db = next(get_db())
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                user.credits = (user.credits or 0) + credits
                db.commit()
                db.refresh(user)
                logger.info(f"Added {credits} credits to user {user_id}")
            else:
                logger.error(f"User {user_id} not found for credit update")

    return JSONResponse(status_code=200, content={"status": "success"})


# Cashfree Payments Endpoints

from pydantic import BaseModel
from payment_gateway.cashfree import (
    CashfreePaymentService,
    CashfreeWebhookHandler,
    CreateOrderRequest,
    CreateOrderResponse,
    PaymentStatusResponse,
    WebhookPayload,
    CashfreePaymentError
)

class CashfreeOrderRequest(BaseModel):
    amount: float
    currency: str

# Initialize Cashfree service
cashfree_service = CashfreePaymentService()
cashfree_webhook = CashfreeWebhookHandler()

# Cashfree Payment Endpoints
@app.post("/api/payment/cashfree/create-order")
async def create_cashfree_order(
    request: CashfreeOrderRequest,
    current_user: models.User = Depends(get_current_user)
) -> CreateOrderResponse:
    """Create a Cashfree payment order"""
    try:
        # Set customer details from user profile
        if not current_user.profile:
            raise HTTPException(
                status_code=400,
                detail="Please complete your profile first"
            )
            
        customer_details = {
            "customer_id": str(current_user.id),
            "customer_name": current_user.profile.name or current_user.email,
            "customer_email": current_user.email,
            "customer_phone": current_user.profile.phone or "0000000000"
        }
        
        # Generate a unique order_id on our end first.
        # This gives us control and guarantees the callback URL is correct.
        import uuid
        order_id = f"order_{int(time.time())}_{str(uuid.uuid4())[:8]}"

        # Store the order_id associated with this user in Redis for fallback
        redis_client = get_redis()
        if redis_client:
            redis_client.setex(
                f"user_order:{current_user.id}",
                1800,  # 30 minutes expiry
                order_id
            )
            logger.info(f"Stored order_id {order_id} for user {current_user.id}")
        
        if os.getenv('PROD_HOST') != "localhost":
            protocol = "https"
        else:
            protocol = "http"

        response = await cashfree_service.create_order(
            amount=request.amount,
            customer_details=customer_details,
            order_meta={
                "return_url": f"{protocol}://{os.getenv('PROD_HOST')}/payment/callback",
                "notify_url": f"{protocol}://{os.getenv('PROD_HOST')}/api/payment/cashfree/webhook"
            },
            order_id=order_id
        )
        
        logger.info(f"Created Cashfree order with ID: {order_id}")
        return response
        
    except CashfreePaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cashfree order creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing error")

@app.post("/api/payment/cashfree/webhook")
async def cashfree_webhook_handler(request: Request):
    """Handle Cashfree payment webhook notifications"""
    try:
        # Get the raw payload and headers
        payload = await request.body()
        signature = request.headers.get("x-webhook-signature") or request.headers.get("x-cf-signature")
        
        logger.info(f"Received webhook with headers: {dict(request.headers)}")
        logger.info(f"Webhook payload: {payload.decode('utf-8')}")
        
        # Parse webhook data to store transaction details
        import json
        webhook_data = json.loads(payload.decode('utf-8'))
        
        if 'data' in webhook_data:
            data = webhook_data['data']
            order_info = data.get('order', {})
            payment_info = data.get('payment', {})
            customer_info = data.get('customer_details', {})
            
            # Extract payment method details
            payment_method_info = payment_info.get('payment_method', {})
            payment_method_display = payment_info.get('payment_group', 'Unknown')
            
            # If it's a card payment, get more details
            if 'card' in payment_method_info:
                card_info = payment_method_info['card']
                card_network = card_info.get('card_network', '').upper()
                card_type = card_info.get('card_type', '').replace('_', ' ').title()
                bank_name = card_info.get('card_bank_name', '')
                payment_method_display = f"{card_network} {card_type}"
                if bank_name:
                    payment_method_display += f" - {bank_name}"
            
            # Calculate credits based on amount
            amount = order_info.get('order_amount', 0)
            if amount == 2250 or amount == 2250.0:  # Pro package
                credits_note = '30 Resume Generation Credits (Pro Package)'
            elif amount == 900 or amount == 900.0:  # Basic package
                credits_note = '10 Resume Generation Credits (Basic Package)'
            elif amount == 5400 or amount == 5400.0:  # Enterprise package
                credits_note = '90 Resume Generation Credits (Enterprise Package)'
            else:  # Default fallback
                credits_note = f'{amount} INR Payment - Credits Package'
            
            # Store transaction details in Redis for retrieval by callback page
            transaction_details = {
                'order_id': order_info.get('order_id'),
                'transaction_id': str(payment_info.get('cf_payment_id')),
                'amount': amount,
                'currency': order_info.get('order_currency', 'INR'),
                'status': payment_info.get('payment_status'),
                'customer_name': customer_info.get('customer_name'),
                'customer_email': customer_info.get('customer_email'),
                'payment_method': payment_method_display,
                'payment_time': payment_info.get('payment_time'),
                'order_note': credits_note,
                'bank_reference': payment_info.get('bank_reference'),
                'card_last_four': payment_method_info.get('card', {}).get('card_number', '').replace('X', '')[-4:] if 'card' in payment_method_info else None
            }
            
            logger.info(f"Storing transaction details: {transaction_details}")
            
            # Store in Redis with order_id as key for 1 hour
            redis_client = get_redis()
            if redis_client:
                redis_client.setex(
                    f"transaction:{order_info.get('order_id')}", 
                    3600,  # 1 hour expiry
                    json.dumps(transaction_details)
                )
                logger.info(f"Transaction details stored in Redis for order: {order_info.get('order_id')}")
            else:
                logger.error("Redis client not available, transaction details not stored")
        
        # Verify the webhook signature (skip for now in development)
        # if not cashfree_webhook.verify_signature(payload, signature):
        #     raise HTTPException(status_code=400, detail="Invalid signature")

        # Process the webhook payload
        await cashfree_webhook.handle_webhook(payload)

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Cashfree webhook error: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        # Return success to avoid webhook retries during development
        return {"status": "error", "message": str(e)}

@app.get("/api/payment/cashfree/status/{order_id}")
async def get_cashfree_payment_status(
    order_id: str,
    current_user: models.User = Depends(get_current_user)
) -> PaymentStatusResponse:
    """Check Cashfree payment status"""
    try:
        return await cashfree_service.get_payment_status(order_id)
    except CashfreePaymentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Cashfree status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment status check failed")

@app.get("/api/payment/transaction/{order_id}")
async def get_transaction_details(order_id: str):
    """Get transaction details from Redis cache"""
    try:
        redis_client = get_redis()
        if redis_client:
            transaction_data = redis_client.get(f"transaction:{order_id}")
            if transaction_data:
                return json.loads(transaction_data)
        
        # If not found in Redis, return basic success info
        return {
            'order_id': order_id,
            'status': 'SUCCESS',
            'order_note': '10 Resume Generation Credits',
            'message': 'Transaction completed successfully'
        }
    except Exception as e:
        logger.error(f"Error retrieving transaction details: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving transaction details")

@app.get("/api/payment/user-order")
async def get_user_stored_order(
    current_user: models.User = Depends(get_current_user)
):
    """Get user's stored order ID from Redis and return transaction details"""
    try:
        redis_client = get_redis()
        if not redis_client:
            raise HTTPException(status_code=500, detail="Redis not available")
        
        # Try to get user's stored order ID
        stored_order_id = redis_client.get(f"user_order:{current_user.id}")
        if stored_order_id:
            stored_order_id = stored_order_id.decode('utf-8') if isinstance(stored_order_id, bytes) else stored_order_id
            logger.info(f"Found stored order ID {stored_order_id} for user {current_user.id}")
            
            # Try to get transaction details for this order
            transaction_data = redis_client.get(f"transaction:{stored_order_id}")
            if transaction_data:
                return json.loads(transaction_data)
            else:
                # Order ID found but no transaction details, return basic success
                return {
                    'order_id': stored_order_id,
                    'status': 'FAILED',
                    'order_note': '',
                    'message': 'Transaction Incomplete'
                }
        
        # No stored order found
        logger.info(f"No stored order found for user {current_user.id}")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving user stored order: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving user order")

@app.get("/api/user/credits")
async def get_user_credits(current_user: models.User = Depends(get_current_user)):
    return {"credits": current_user.credits or 0}

@app.post("/api/user/update-credits")
async def update_user_credits(
    amount: int = Form(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user credits and return updated balance"""
    current_user.credits = (current_user.credits or 0) + amount
    db.commit()
    db.refresh(current_user)
    return {"credits": current_user.credits}

# Update resume generation to check and deduct credits
@app.post("/api/generate-resume")
async def generate_resume_endpoint(
    job_description: UploadFile = File(...),
    skills: Optional[List[str]] = None,
    template_id: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Main endpoint to generate optimized resume content from a job description."""
    # Check credits
    if (current_user.credits or 0) < 1:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits. Please purchase credits to generate resumes."
        )

    start_time = time.time()
    # Get user profile
    if not current_user.profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete your profile before generating a resume"
        )
    
    # Check if in dev mode (PROD_MODE=False)
    if os.getenv("PROD_MODE", "True").lower() == "false":
        # Get latest resume from database
        latest_resume = db.query(models.Resume)\
            .filter(models.Resume.profile_id == current_user.profile.id)\
            .order_by(models.Resume.created_at.desc())\
            .first()
        
        if latest_resume:
            return {
                "job_title": "Cached Resume",
                "content": latest_resume.content,
                "agent_outputs": "Using cached resume in dev mode",
                "token_usage": {},
                "total_usage": {},
                "message": "Returning cached resume content (PROD_MODE=False)"
            }
    
    profile = current_user.profile
    current_uuid = generate_uuid()
    # Step 1: Read and process the job description
    job_desc_text = await read_job_description(job_description)
    
    # Step 2: Extract the job title
    job_title = extract_job_title(job_desc_text)
    
    # Save job title to Redis cache
    save_job_title_to_cache(current_uuid, job_title, expiration=1800)
    
    # Step 3: Build parsed_data from profile sections
    parsed_data = {
        "professional_summary": profile.summary or "Not specified",
        "past_experiences": [
            {
                "position": exp.position,
                "company": exp.company,
                "start_date": exp.start_date.isoformat() if exp.start_date else None,
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "description": exp.description,
            }
            for exp in profile.work_experiences
        ],
        "skills": [skill.name for skill in profile.skills],
        "education": [
            {
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_date": edu.start_date.isoformat() if edu.start_date else None,
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
            }
            for edu in profile.educations
        ],
        "certifications": [] # Assuming no certifications are stored in the profile
    }
    
    # Step 4: Generate optimized resume content with timeout
    resume_generator = ResumeGenerator()
    try:
        optimized_data = await asyncio.wait_for(
            resume_generator.optimize_resume(current_uuid, parsed_data, job_desc_text, skills, current_user.id), # type: ignore
            timeout=600  # 10 minute timeout
        )
        
        # Deduct 1 credit after successful generation
        current_user.credits = (current_user.credits or 0) - 1
        db.commit()
        db.refresh(current_user)
        logger.info(f"Deducted 1 credit from user {current_user.id}. Remaining credits: {current_user.credits}")
        
    except asyncio.TimeoutError:
        logger.error("Resume generation timed out")
        raise HTTPException(
            status_code=504,
            detail="Resume generation took too long. Please try again with a simpler job description."
        )
    
    time_taken = time.time() - start_time
    logger.info(f"Successfully Generated AI Optimised Resume in : {time_taken:.6f} secs")
    return {
        "job_title": job_title,
        "content": optimized_data['ai_content'],
        "agent_outputs": optimized_data['agent_outputs'],
        "token_usage": optimized_data['token_usage'],
        "total_usage": optimized_data['total_usage'],
        "message": "Resume generated successfully"
    }
