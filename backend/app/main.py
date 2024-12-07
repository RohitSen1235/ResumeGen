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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)
logger.info(f"Loading environment from: {env_path}")

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

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LaTeX processor
latex_processor = LatexProcessor()

# Configure Groq client
logger.info("Checking Groq API key configuration...")

if api_key == "your_api_key_here":
    logger.error("GROQ_API_KEY is set to default value")
    raise HTTPException(
        status_code=500,
        detail="Please replace the default API key in .env with your actual Groq API key."
    )

try:
    logger.info("Initializing Groq client...")
    groq_client = groq.Groq(api_key=api_key)
    logger.info(f"Groq client initialized successfully with model: {model_name}")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}\n{traceback.format_exc()}")
    raise HTTPException(
        status_code=500,
        detail=f"Failed to initialize Groq client: {str(e)}"
    )

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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to get access token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/user", response_model=schemas.User)
def get_current_user_data(current_user: models.User = Depends(get_current_user)):
    """Get current user data."""
    return current_user

# Profile endpoints
@app.post("/api/profile", response_model=schemas.Profile)
def create_profile(
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
def get_profile(
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
def update_profile(
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
    """Upload a resume file."""
    try:
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )

        # Create uploads directory if it doesn't exist
        upload_dir = Path(__file__).parent / "uploads"
        upload_dir.mkdir(exist_ok=True)

        # Generate unique filename using user ID and timestamp
        timestamp = int(time.time())
        filename = f"resume_{current_user.id}_{timestamp}.pdf"
        file_path = upload_dir / filename

        # Save the file
        content = await resume.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Update profile with resume path
        if not current_user.profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        current_user.profile.resume_path = str(file_path)
        db.commit()

        return {"path": str(file_path)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading resume: {str(e)}"
        )

@app.get("/api/resume/{filename}")
async def get_resume(
    filename: str,
    current_user: models.User = Depends(get_current_user)
):
    """Get uploaded resume file."""
    try:
        if not current_user.profile or not current_user.profile.resume_path:
            raise HTTPException(
                status_code=404,
                detail="No resume found"
            )

        file_path = Path(current_user.profile.resume_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Resume file not found"
            )

        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving resume: {str(e)}"
        )

# Resume generation endpoints
async def read_job_description(job_description: UploadFile) -> str:
    """Read and decode the job description file content."""
    try:
        logger.info(f"Reading job description file: {job_description.filename}")
        logger.info(f"File content type: {job_description.content_type}")
        
        content = await job_description.read()
        logger.info(f"Raw content length: {len(content)} bytes")
        
        # Try different encodings
        try:
            job_desc_text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                job_desc_text = content.decode("latin-1")
                logger.info("Successfully decoded using latin-1 encoding")
            except:
                job_desc_text = content.decode("utf-8", errors="ignore")
                logger.info("Decoded using UTF-8 with ignore parameter")
        
        logger.info(f"Job description content length: {len(job_desc_text)} characters")
        
        if len(job_desc_text.strip()) == 0:
            raise ValueError("Job description file is empty")
            
        return job_desc_text
        
    except Exception as e:
        logger.error(f"Error reading job description file: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=400,
            detail=f"Error reading job description file: {str(e)}"
        )

def extract_job_title(text: str) -> str:
    """Extract job title from job description using Groq."""
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a job title extractor. Extract only the main job title/role from the given job description. Return only the title, nothing else."},
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

def generate_resume_content(job_desc_text: str) -> str:
    """Generate resume content using Groq API."""
    try:
        system_message = """You are an expert resume writer specializing in creating unique, tailored resumes. Your task is to:

1. Thoroughly analyze the job description to understand:
   - Core responsibilities and objectives
   - Required technical skills and competencies
   - Desired soft skills and qualities
   - Industry context and company needs

2. Generate a resume that:
   - Demonstrates deep understanding of the role's requirements
   - Uses natural, professional language (avoid copying phrases directly from the job description)
   - Focuses on relevant achievements and capabilities
   - Maintains ATS-friendliness while being authentic
   - Shows career progression and skill development

Format the resume with these sections:
- Professional Summary (compelling overview aligned with the role)
- Key Skills (relevant technical and soft skills, naturally presented)
- Professional Experience (previous roles, past achievements, demonstrating relevant capabilities)
- Successfull Projects (Optional, only provide if relevant)
- Education (relevant qualifications and certifications, provide placeholders if not present)

Important: Do not copy phrases directly from the job description. Instead, understand the requirements and express them naturally in the context of the candidate's experience."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Please create a tailored resume based on understanding this job description:\n\n{job_desc_text}"}
        ]
        
        logger.info(f"Sending request to Groq API using model: {model_name}")
        completion = groq_client.chat.completions.create(
            messages=messages,
            model=model_name,
            temperature=0.5,
            max_tokens=1500
        )
        logger.info("Successfully received response from Groq API")
        
        generated_resume = completion.choices[0].message.content
        if not generated_resume.strip():
            raise ValueError("Generated resume is empty")
            
        logger.info(f"Generated resume length: {len(generated_resume)} characters")
        return generated_resume
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating resume content: {error_msg}\n{traceback.format_exc()}")
        
        if "rate limit" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        elif "invalid api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid or unauthorized API key. Please check your Groq API key configuration."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating resume content: {error_msg}"
            )

def create_pdf_resume(generated_resume: str, job_title: str, personal_info: dict) -> Optional[str]:
    """Generate PDF version of the resume."""
    try:
        logger.info("Generating PDF resume...")
        
        formatted_content = latex_processor.format_content(personal_info, generated_resume, job_title)
        pdf_path = latex_processor.generate_resume_pdf(formatted_content)
        
        if not os.path.exists(pdf_path):
            logger.error("PDF file does not exist at the expected location.")
            return None
        
        pdf_url = f"/api/download-resume/{os.path.basename(pdf_path)}"
        logger.info(f"PDF generated successfully: {pdf_path}")
        return pdf_url
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}\n{traceback.format_exc()}")
        return None

@app.post("/api/generate-resume")
async def generate_resume(
    job_description: UploadFile = File(...),
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
        logger.info(f"Extracted job title: {job_title}")
        
        # Step 3: Generate the resume content
        generated_resume = generate_resume_content(job_desc_text)
        
        # Step 4: Create PDF version
        pdf_url = create_pdf_resume(generated_resume, job_title, personal_info)
        
        # Step 5: Return the response
        return {
            "content": generated_resume,
            "job_title": job_title,
            "pdf_url": pdf_url,
            "message": "Resume generated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in generate_resume: {str(e)}\n{traceback.format_exc()}")
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

@app.get("/api/health")
async def health_check():
    try:
        logger.info("Performing health check...")
        # Test Groq client connection
        groq_client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model=model_name,
            max_tokens=1
        )
        logger.info("Health check successful")
        return {
            "status": "healthy", 
            "groq_api": "connected",
            "model": model_name
        }
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Health check failed - Error: {error_msg}\n{traceback.format_exc()}")
        return {
            "status": "unhealthy",
            "error": error_msg,
            "type": "api_error",
            "model": model_name
        }
