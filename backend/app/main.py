from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
import groq
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
from .database import get_db
from . import models, schemas
from .utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
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

# Initialize Groq client
groq_client = groq.Groq(api_key=api_key)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
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
                detail="Incorrect email or password",
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
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
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

        # Create uploads directory if it doesn't exist
        upload_dir = Path(__file__).parent / "uploads"
        upload_dir.mkdir(exist_ok=True)

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
    try:
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
        
        # Step 1: Read and process the job description
        job_desc_text = await read_job_description(job_description)
        
        # Step 2: Extract the job title
        job_title = extract_job_title(job_desc_text)
        
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
            parsed_data = {
                "professional_summary": "Not specified",
                "past_experiences": [],
                "skills": [],
                "education": [],
                "certifications": []
            }
        
        # Step 4: Generate optimized resume content
        resume_generator = ResumeGenerator()
        optimized_data = resume_generator.optimize_resume(parsed_data, job_desc_text, skills)
        
        # Step 5: Generate PDF using LaTeX processor
        pdf_path, usage_stats = await resume_generator.generate_resume_pdf(
            resume_data=optimized_data,
            personal_info=personal_info,
            job_title=job_title
        )
        
        if not pdf_path:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF resume"
            )
        
        pdf_url = f"/api/download-resume/{os.path.basename(pdf_path)}"
        
        return {
            "job_title": job_title,
            "pdf_url": pdf_url,
            "content": optimized_data['ai_content'],
            "token_usage": optimized_data['token_usage'],
            "total_usage": optimized_data['total_usage'],
            "message": "Resume generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_resume: {str(e)}")
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
