import fitz
import groq
import os
import logging

logger = logging.getLogger(__name__)

def extract_text_with_fitz(file_path):
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        logger.info("Successfully read resume file")
        return text
    except Exception as e:
        logger.error(f"Failed to read resume file: {e}")
        return f"An error occurred: {e}"

def parse_pdf_resume(file_path):
    try:
        # Extract text from PDF
        text = extract_text_with_fitz(file_path)
        if text.startswith("An error occurred"):
            return {"error": text}

        # Initialize Groq client
        client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        logger.info("Successfully validated Groq API key")

        # Craft the prompt for Groq
        prompt = f"""
        Analyze the following resume text and categorize it into distinct sections. 
        For each section, extract relevant information and present it in a clear format.
        
        Resume text:
        {text}
        
        Please categorize the information into these sections and return them in JSON format:
        {{
            "Professional Summary": "summary text here",
            "Past Experiences": ["experience 1", "experience 2", ...],
            "Skills": ["skill 1", "skill 2", ...],
            "Projects":["project 1","project 2, ...],
            "Education": ["education 1", "education 2", ...],
            "Certifications": ["cert 1", "cert 2", ...],
            "Others" : [All Other information...],
        }}
        
        If a category has no relevant information, use an empty list [] or empty string "" as appropriate.
        """

        # Make the API call to Groq
        response = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model=os.getenv("GROQ_MODEL"),  # Using Mixtral model for better comprehension
            temperature=0.1,  # Low temperature for more focused responses
        )

        # Extract the parsed content
        parsed_content = response.choices[0].message.content

        try:
            # Try to evaluate the string as a Python dictionary
            # This is safer than using eval() directly
            import ast
            structured_content = ast.literal_eval(parsed_content)
            
            # Process the response into our expected format
            result = {
                "professional_summary": structured_content.get("Professional Summary", "Not specified"),
                "past_experiences": structured_content.get("Past Experiences", []),
                "skills": structured_content.get("Skills", []),
                "Projects": structured_content.get("Projects", []),
                "education": structured_content.get("Education", []),
                "certifications": structured_content.get("Certifications", []),
                "Others": structured_content.get("Others", []),
            }
        except (SyntaxError, ValueError) as e:
            # If we can't parse the JSON, create a basic structure from the raw text
            logger.warning(f"Could not parse structured content: {e}. Using raw text format.")
            result = {
                "professional_summary": parsed_content,
                "past_experiences": [],
                "skills": [],
                "projects":[],
                "education": [],
                "certifications": [],
                "others":[]
            }
        
        logger.info(f"Successfully parsed resume sections: {list(result.keys())}")
        return result

    except Exception as e:
        logger.error(f"An error occurred during resume parsing: {str(e)}")
        return {"error": f"An error occurred during resume parsing: {str(e)}"}

def parse_resume(file_path):
    """Alias for parse_pdf_resume to maintain backward compatibility"""
    return parse_pdf_resume(file_path)
