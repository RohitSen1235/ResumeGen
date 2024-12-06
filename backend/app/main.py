from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import groq
from groq.types.chat import ChatCompletion
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import logging
import json
import traceback
import re

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

class ResumeResponse(BaseModel):
    content: str
    job_title: str
    message: Optional[str] = None

def extract_job_title(text: str) -> str:
    """Extract job title from job description using Groq."""
    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a job title extractor. Extract only the main job title/role from the given job description. Return only the title, nothing else."},
                {"role": "user", "content": f"Extract the main job title from this job description:\n\n{text}"}
            ],
            model=model_name,
            temperature=0.3,
            max_tokens=50
        )
        job_title = completion.choices[0].message.content.strip()
        # Clean up the job title
        job_title = re.sub(r'[^\w\s-]', '', job_title)
        job_title = job_title.replace(' ', '-').lower()
        return job_title
    except Exception as e:
        logger.error(f"Error extracting job title: {str(e)}")
        return "position"

@app.post("/api/generate-resume")
async def generate_resume(job_description: UploadFile = File(...)):
    try:
        # Log the start of processing
        logger.info(f"Processing job description file: {job_description.filename}")
        logger.info(f"File content type: {job_description.content_type}")
        
        # Read and decode file content
        try:
            content = await job_description.read()
            logger.info(f"Raw content length: {len(content)} bytes")
            
            # Try to decode with different encodings if UTF-8 fails
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
                logger.error("Empty job description file")
                raise HTTPException(
                    status_code=400,
                    detail="Job description file is empty"
                )
            
        except Exception as e:
            logger.error(f"Error reading job description file: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=400,
                detail=f"Error reading job description file: {str(e)}"
            )
        
        # Extract job title first
        job_title = extract_job_title(job_desc_text)
        logger.info(f"Extracted job title: {job_title}")

        # Create a system message that instructs the model on resume generation
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
- Professional Experience (achievement-focused, demonstrating required capabilities)
- Education (relevant qualifications and certifications)

Important: Do not copy phrases directly from the job description. Instead, understand the requirements and express them naturally in the context of the candidate's experience."""

        logger.info("Preparing Groq API request for resume generation...")
        
        # Create the chat completion request using Groq
        try:
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Please create a tailored resume based on understanding this job description:\n\n{job_desc_text}"}
            ]
            
            logger.info(f"Sending request to Groq API using model: {model_name}")
            completion = groq_client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=0.7,
                max_tokens=1500
            )
            logger.info("Successfully received response from Groq API")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Groq API error: {error_msg}\n{traceback.format_exc()}")
            
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
                    detail=f"Groq API error: {error_msg}"
                )
        
        # Extract the generated resume from the response
        try:
            generated_resume = completion.choices[0].message.content
            logger.info("Successfully extracted resume content")
            logger.info(f"Generated resume length: {len(generated_resume)} characters")
            
            if not generated_resume.strip():
                logger.error("Generated resume is empty")
                raise HTTPException(
                    status_code=500,
                    detail="Generated resume is empty"
                )
            
        except Exception as e:
            logger.error(f"Error extracting resume content: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing Groq response: {str(e)}"
            )
        
        return ResumeResponse(
            content=generated_resume,
            job_title=job_title,
            message="Resume generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in generate_resume: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

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
