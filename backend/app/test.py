import os
import pytest
from .utils.resume_parser import parse_pdf_resume

@pytest.fixture
def sample_resume_path():
    return f"/home/rohit/Workspace/resume_builder/backend/app/uploads/resume_1_1733606994.pdf"

def test_parse_pdf_resume(sample_resume_path):
    # Set up Groq API key if not already set
    if "GROQ_API_KEY" not in os.environ:
        pytest.skip("GROQ_API_KEY environment variable not set")
    
    # Parse the resume
    result = parse_pdf_resume(sample_resume_path)
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "professional_summary" in result
    assert "past_experiences" in result
    assert "skills" in result
    assert "education" in result
    assert "certifications" in result
    
    # Verify at least some content was extracted
    assert any(result.values()), "No content was extracted from the resume"
