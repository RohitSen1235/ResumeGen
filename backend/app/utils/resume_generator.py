import groq
import os
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import json
from pathlib import Path
from ..latex.processor import LatexProcessor
import tiktoken

logger = logging.getLogger(__name__)

class TokenTracker:
    """Tracks token usage and calculates costs for Groq API calls"""
    
    COST_PER_MILLION_TOKENS = 20.0  # $20 per million tokens
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.session_history = []
        self.encoder = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's tokenizer as approximation
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in a string using the tokenizer"""
        return len(self.encoder.encode(text))
    
    def add_api_call(self, prompt: str, response: str) -> Dict[str, Any]:
        """Record a new API call with input and output tokens"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(response)
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        call_stats = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': self.calculate_cost(input_tokens),
            'output_cost': self.calculate_cost(output_tokens),
            'total_cost': self.calculate_cost(input_tokens + output_tokens)
        }
        
        self.session_history.append(call_stats)
        return call_stats
    
    def calculate_cost(self, num_tokens: int) -> float:
        """Calculate cost in dollars for a given number of tokens"""
        return (num_tokens / 1_000_000) * self.COST_PER_MILLION_TOKENS * 10
    
    def get_total_usage(self) -> Dict[str, Any]:
        """Get total token usage and costs for all API calls"""
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'total_input_cost': self.calculate_cost(self.total_input_tokens),
            'total_output_cost': self.calculate_cost(self.total_output_tokens),
            'total_cost': self.calculate_cost(self.total_input_tokens + self.total_output_tokens),
            'call_history': self.session_history
        }

class ResumeGenerator:
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.latex_processor = LatexProcessor()
        self.token_tracker = TokenTracker()
        # Validate Groq API on initialization
        try:
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="mixtral-8x7b-32768",
                max_tokens=1
            )
            logger.info("Successfully validated Groq API connection")
        except Exception as e:
            logger.error(f"Failed to validate Groq API: {str(e)}")
            raise

    def format_experiences(self, experiences: List[str]) -> str:
        """Format experiences into a readable string."""
        if not experiences:
            return "No previous experience provided"
        return "\n".join([f"- {exp}" for exp in experiences])

    def format_education(self, education: List[str]) -> str:
        """Format education into a readable string."""
        if not education:
            return "No education information provided"
        return "\n".join([f"- {edu}" for edu in education])

    def format_skills(self, skills: List[str]) -> str:
        """Format skills into a readable string."""
        if not skills:
            return "No skills provided"
        return ", ".join(skills)

    def generate_optimized_resume(self, professional_info: Dict[str, Any], job_description: str, skills: Optional[List[str]] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Generate an optimized resume content using Groq AI and track token usage.
        Returns both the generated content and token usage statistics.
        """
        try:
            # Log input data structure
            logger.info(f"Input data structure for optimization: {json.dumps(professional_info, indent=2)}")

            # Format the professional info for the prompt
            experience_text = self.format_experiences(professional_info.get('past_experiences', []))
            education_text = self.format_education(professional_info.get('education', []))
            skills_text = self.format_skills(professional_info.get('skills', []))
            summary_text = professional_info.get('professional_summary', 'Not provided')
            certifications_text = "\n".join([f"- {cert}" for cert in professional_info.get('certifications', [])])

            # Construct the prompt
            prompt = f"""
            As an expert resume writer, create an optimized resume for the job description provided.
            If no previous experience is provided, create compelling fictional experience that would be ideal for this role.
            Focus on relevant experience and skills that match the job requirements.
            Consider the following skills if provided: {skills}.
            
            Note: When no previous experience exists, generate 2-3 relevant positions with achievements that demonstrate
            the key skills and qualifications needed for the target role.

            Original Professional Information:

            Current Summary:
            {summary_text}

            Experience:
            {experience_text}

            Education:
            {education_text}

            Skills:
            {skills_text}

            Certifications:
            {certifications_text}

            Job Description:
            {job_description}

            Generate an optimized resume with the following sections.
            Use the exact format shown below, including the section headers and markers:

            # Professional Summary
            ===
            Write 2-3 compelling sentences highlighting most relevant qualifications.
            ===

            # Key Skills
            ===
            List 8-10 most relevant skills, each on a new line starting with •
            Example:
            • Skill 1
            • Skill 2
            ===

            # Professional Experience
            ===
            For each position, format as:
            [Title] at [Company], [Duration]
            • Achievement 1
            • Achievement 2
            • Achievement 3
            • Achievement 4

            Example:
            Senior Software Engineer at XYZ Corp, 2020-Present
            • Led development of microservices architecture
            • Implemented automated testing pipeline
            ===

            # Education
            ===
            For each education entry, format as:
            [Degree]
            [Institution]
            [Year]

            Example:
            Bachelor of Science in Computer Science
            University of California, Berkeley
            2014
            ===

            # Certifications
            ===
            List relevant certifications, each on a new line starting with •
            Example:
            • AWS Certified Solutions Architect
            • Professional Scrum Master I
            ===

            Important:
            1. Keep the exact section headers (# Section Name)
            2. Keep the === markers before and after each section's content
            3. For Key Skills and Certifications, prefix each item with • and put each on a new line
            4. Make the content highly relevant to the job description
            5. Follow the exact formatting shown in the examples
            6. If a section has no content, include the section with 'None' between the === markers
            """

            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume writer who specializes in creating targeted resumes that align with specific job descriptions. When no previous experience is provided, create compelling fictional experience that would be ideal for the job description. Always format your response exactly as requested, maintaining section headers and markers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                stream=False
            )

            # Extract the generated content
            generated_content = chat_completion.choices[0].message.content

            # Track token usage
            usage_stats = self.token_tracker.add_api_call(prompt, generated_content)

            logger.info("Optimized resume generated by AI:\n" + generated_content)
            logger.info(f"Token usage for this generation: {json.dumps(usage_stats, indent=2)}")

            return generated_content, usage_stats

        except Exception as e:
            logger.error(f"Error generating optimized resume: {str(e)}")
        raise

    def optimize_resume(self, professional_info: Dict[str, Any], job_description: str, skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Main function to optimize the entire resume using Groq AI.
        Returns the optimized content along with token usage statistics.
        """
        try:
            # Generate optimized content and get usage stats
            optimized_content, usage_stats = self.generate_optimized_resume(professional_info, job_description, skills)

            return {
                'ai_content': optimized_content,
                'professional_info': professional_info,
                'token_usage': usage_stats,
                'total_usage': self.token_tracker.get_total_usage()
            }

        except Exception as e:
            logger.error(f"Error optimizing resume: {str(e)}")
            raise

    async def generate_resume_pdf(self, resume_data: Dict[str, Any], personal_info: Dict[str, Any], 
                                job_title: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a PDF resume using LaTeX.
        Returns both the PDF path and token usage statistics.
        """
        try:
            # Format the content for the LaTeX template
            formatted_content = self.latex_processor.format_content(
                personal_info=personal_info,
                ai_content=resume_data['ai_content'],
                job_title=job_title
            )

            # Generate PDF using LaTeX processor
            pdf_path = self.latex_processor.generate_resume_pdf(formatted_content)
            logger.info(f"Successfully generated PDF resume at: {pdf_path}")
            
            # Get the total token usage statistics
            total_usage = self.token_tracker.get_total_usage()
            
            return pdf_path, total_usage

        except Exception as e:
            logger.error(f"Error generating PDF resume: {str(e)}")
            raise
