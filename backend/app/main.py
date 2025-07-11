
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, status
import sqlalchemy.exc
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
import groq
from .database import get_redis
from typing import Optional, Tuple
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
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_token
)

from .utils.email import send_email
from .utils.resume_generator import ResumeGenerator
from .utils.resume_parser import parse_pdf_resume
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

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "https://resumegenie.rsfreelance.com"],
    allow_credentials=True,
    allow_methods=["*"],
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
        to_email=user.email,
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
        user.hashed_password = get_password_hash(request.new_password)
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
        if not verify_password(form_data.password, user.hashed_password):
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
        return {"access_token": access_token, "token_type": "bearer"}
        
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
    
    for key, value in profile.dict(exclude_unset=True).items():
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

        # Create uploads directory if it doesn't exist (use Docker container path)
        upload_dir = Path("/app/uploads")
        upload_dir.mkdir(exist_ok=True)
        logger.info(f"Using uploads directory: {upload_dir}")

        # Delete existing resume file if it exists
        if current_user.profile.resume_path:
            existing_file = Path(current_user.profile.resume_path)
            logger.info(f"Checking existing resume file at: {existing_file.absolute()}")
            if existing_file.exists():
                logger.info(f"Deleting existing resume file: {existing_file}")
                try:
                    existing_file.unlink()
                    logger.info("Successfully deleted old resume file")
                except Exception as e:
                    logger.error(f"Error deleting old resume file: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error deleting old resume file: {str(e)}"
                    )

        # Generate unique filename
        timestamp = int(time.time())
        filename = f"resume_{current_user.id}_{timestamp}.pdf"
        file_path = upload_dir / filename

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            content = await resume.read()
            buffer.write(content)

        # Update profile with resume path
        current_user.profile.resume_path = str(file_path)

        # Parse resume and update professional info if possible
        try:
            parsed_data = parse_pdf_resume(str(file_path))
            if isinstance(parsed_data, dict) and "error" not in parsed_data:
                current_user.profile.professional_info = parsed_data
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            # Continue even if parsing fails

        db.commit()
        return {"message": "Resume uploaded successfully", "file_path": str(file_path)}

    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading resume: {str(e)}"
        )

# Resume generation endpoints
from typing import List, Optional

@app.post("/api/generate-resume")
async def generate_resume_endpoint(
    job_description: UploadFile = File(...),
    skills: Optional[List[str]] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Main endpoint to generate a resume from a job description."""

    # Get user profile
    if not current_user.profile:
        raise HTTPException(
            status_code=400,
            detail="Please complete your profile before generating a resume"
        )
    
    profile = current_user.profile
    personal_info = {
        "name": profile.name,
        "email": current_user.email,
        "phone": profile.phone,
        "location": profile.location,
        "linkedin": profile.linkedin_url
    }
    current_uuid = generate_uuid()
    # Step 1: Read and process the job description
    job_desc_text = await read_job_description(job_description)
    
    # Step 2: Extract the job title
    job_title = extract_job_title(job_desc_text)
    
    # Save job title to Redis cache
    save_job_title_to_cache(current_uuid, job_title, expiration=1800)
    
    # Step 3: Parse existing resume if available
    if profile.resume_path and os.path.exists(profile.resume_path):
        try:
            parsed_data = parse_pdf_resume(profile.resume_path)
            if isinstance(parsed_data, dict) and "error" not in parsed_data:
                logger.info(f"Successfully parsed resume sections: {list(parsed_data.keys())}")
            else:
                logger.error(f"Error parsing resume: {parsed_data.get('error', 'Unknown error')}")
                parsed_data = {
                    "professional_summary": "Not specified",
                    "past_experiences": [],
                    "skills": [],
                    "education": [],
                    "certifications": []
                }
        except Exception as e:
            logger.error(f"Error processing existing resume: {str(e)}")
            parsed_data = {
                "professional_summary": "Not specified",
                "past_experiences": [],
                "skills": [],
                "education": [],
                "certifications": []
            }
    else:
        # If no resume is uploaded, use empty data to let Groq generate new content
        parsed_data = {
            "professional_summary": "Not specified",
            "past_experiences": [],
            "skills": [],
            "education": [],
            "certifications": []
        }
    
    # Step 4: Generate optimized resume content
    resume_generator = ResumeGenerator()
    optimized_data = await resume_generator.optimize_resume(current_uuid,parsed_data, job_desc_text, skills, current_user.id)
    
    # Step 5: Generate PDF using LaTeX processor
    pdf_path, usage_stats = await resume_generator.generate_resume(
        resume_data=optimized_data,
        personal_info=personal_info,
        job_title=job_title,
        format='pdf'
    )
    
    if not pdf_path:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate PDF resume"
        )
    
    pdf_url = f"/download-resume/{os.path.basename(pdf_path)}"
    
    return {
        "job_title": job_title,
        "pdf_url": pdf_url,
        "content": optimized_data['ai_content'],
        "agent_outputs": optimized_data['agent_outputs'],
        "token_usage": optimized_data['token_usage'],
        "total_usage": optimized_data['total_usage'],
        "message": "Resume generated successfully"
    }

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
            "location": profile.location,
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
        
        docx_url = f"/api/download-resume/{os.path.basename(docx_path)}"
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
            model=model_name,
            temperature=0.7,
            max_tokens=30
        )
        job_title = completion.choices[0].message.content.strip()
        # Clean up the job title
        job_title = re.sub(r'[^\w\s-]', '', job_title)
        job_title = job_title.replace(' ', '-').lower()
        return job_title
    except Exception as e:
        logger.error(f"Error extracting job title: {str(e)}")
        return "position"

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
    
    return {
        "id": str(resume.id),
        "name": resume.name,
        "version": resume.version,
        "content": resume.content,
        "job_description": resume.job_description,
        "status": resume.status,
        "created_at": resume.created_at.isoformat(),
        "updated_at": resume.updated_at.isoformat() if resume.updated_at else None
    }

@app.delete("/api/delete-resume")
async def delete_resume(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user's uploaded resume."""
    try:
        if not current_user.profile or not current_user.profile.resume_path:
            raise HTTPException(
                status_code=404,
                detail="No resume found"
            )

        # Delete the file if it exists
        file_path = Path(current_user.profile.resume_path)
        if file_path.exists():
            file_path.unlink()

        # Clear the resume path in profile
        current_user.profile.resume_path = None
        db.commit()

        return {"message": "Resume deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting resume: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    try:
        # Test Groq client connection
        groq_client = groq.Groq(api_key=api_key)
        groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model=model_name,
            max_tokens=1
        )
        logger.info("Groq API connection validated")
        return {
            "status": "healthy", 
            "groq_api": "connected",
            "model": model_name
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Groq API validation failed: {error_msg}")
        return {
            "status": "unhealthy",
            "error": error_msg,
            "type": "api_error",
            "model": model_name
        }
