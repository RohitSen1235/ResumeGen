import os
import json
from typing import Dict, Any
from groq import Groq
from ..schemas import ResumeParseResponse

class GroqResumeParser:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def parse_resume(self, resume_text: str) -> ResumeParseResponse:
        """
        Parse resume text using Groq AI and return structured data
        """
        prompt = self._create_parsing_prompt(resume_text)
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume parser. Extract structured information from resumes and return valid JSON only. Do not include any explanatory text, markdown formatting, or code blocks - just pure JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=os.getenv("GROQ_MODEL"),
                temperature=0.1,
                max_tokens=4000,
            )
            
            response_text = chat_completion.choices[0].message.content
            print(f"Groq raw response: {response_text[:200]}...")  # Debug log
            
            if not response_text or response_text.strip() == "":
                print("Empty response from Groq")
                return ResumeParseResponse()
            
            # Clean the response text - remove markdown code blocks if present
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # Parse the JSON response
            parsed_data = json.loads(cleaned_response)
            
            # Clean up proficiency values before validation
            self._clean_skill_proficiency(parsed_data)

            # Convert to Pydantic model
            return ResumeParseResponse(**parsed_data)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {response_text}")
            # Return empty response on JSON error
            return ResumeParseResponse()
        except Exception as e:
            print(f"Error parsing resume with Groq: {e}")
            # Return empty response on error
            return ResumeParseResponse()

    def _clean_skill_proficiency(self, data: Dict[str, Any]):
        if "skills" in data and isinstance(data["skills"], list):
            for skill in data["skills"]:
                if "proficiency" in skill and isinstance(skill["proficiency"], str):
                    proficiency = skill["proficiency"].strip().lower()
                    if proficiency == "basic":
                        skill["proficiency"] = "Beginner"
    
    def _create_parsing_prompt(self, resume_text: str) -> str:
        return f"""
Extract structured information from the following resume text and return ONLY valid JSON in the exact format specified below. Do not include any explanatory text, just the JSON.

Resume Text:
{resume_text}

Return JSON in this exact format:
{{
  "work_experience": [
    {{
      "position": "Job Title",
      "company": "Company Name",
      "location": "City, State/Country",
      "start_date": "YYYY-MM-DD or null",
      "end_date": "YYYY-MM-DD or null",
      "current_job": true/false,
      "description": "Job description",
      "achievements": ["Achievement 1", "Achievement 2"],
      "technologies": ["Tech 1", "Tech 2"]
    }}
  ],
  "education": [
    {{
      "institution": "University/School Name",
      "degree": "Degree Type",
      "field_of_study": "Field of Study",
      "location": "City, State/Country",
      "start_date": "YYYY-MM-DD or null",
      "end_date": "YYYY-MM-DD or null",
      "gpa": 3.5 or null,
      "description": "Additional details",
      "achievements": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "skills": [
    {{
      "name": "Skill Name",
      "category": "Programming/Languages/Tools/etc",
      "proficiency": "Only use one of: 'Beginner', 'Intermediate', 'Advanced', 'Expert', or null",
      "years_experience": 5 or null
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Project description",
      "url": "https://project-url.com or null",
      "github_url": "https://github.com/user/repo or null",
      "start_date": "YYYY-MM-DD or null",
      "end_date": "YYYY-MM-DD or null",
      "technologies": ["Tech 1", "Tech 2"],
      "achievements": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "publications": [
    {{
      "title": "Publication Title",
      "publisher": "Publisher Name",
      "publication_date": "YYYY-MM-DD or null",
      "url": "https://publication-url.com or null",
      "description": "Publication description",
      "authors": ["Author 1", "Author 2"]
    }}
  ],
  "volunteer_work": [
    {{
      "organization": "Organization Name",
      "role": "Volunteer Role",
      "cause": "Cause/Mission",
      "location": "City, State/Country",
      "start_date": "YYYY-MM-DD or null",
      "end_date": "YYYY-MM-DD or null",
      "current_role": true/false,
      "description": "Role description",
      "achievements": ["Achievement 1", "Achievement 2"]
    }}
  ],
  "summary": "Professional summary or objective",
  "professional_title": "Current/Desired Job Title"
}}

Important notes:
- Use null for missing dates, not empty strings
- Extract as much detail as possible from the resume
- Group similar skills by category
- Include quantifiable achievements where possible
- For dates, try to parse them into YYYY-MM-DD format, use null if unclear
- Return ONLY the JSON, no additional text
"""
