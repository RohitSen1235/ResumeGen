import groq
import os
import time
import logging
from typing import Dict, Any, List
import json
from pathlib import Path
from ..latex.processor import LatexProcessor

logger = logging.getLogger(__name__)

class ResumeGenerator:
    def __init__(self):
        self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.latex_processor = LatexProcessor()
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

    def generate_optimized_resume(self, professional_info: Dict[str, Any], job_description: str) -> str:
        """
        Generate an optimized resume content using Groq AI based on the parsed resume data
        and job description.
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
            As an expert resume writer, optimize the following professional information for the job description provided.
            Focus on relevant experience and skills, and create a compelling professional summary.
            
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
                        "content": "You are an expert resume writer who specializes in creating targeted resumes that align with specific job descriptions. Always format your response exactly as requested, maintaining section headers and markers."
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

            # Extract and return the generated content
            generated_content = chat_completion.choices[0].message.content
            logger.info("Optimized resume generated by AI:\n" + generated_content)
            return generated_content

        except Exception as e:
            logger.error(f"Error generating optimized resume: {str(e)}")
            raise

    def optimize_resume(self, professional_info: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Main function to optimize the entire resume using Groq AI.
        """
        try:
            # Generate optimized content
            optimized_content = self.generate_optimized_resume(professional_info, job_description)
            
            return {
                'ai_content': optimized_content,
                'professional_info': professional_info
            }

        except Exception as e:
            logger.error(f"Error optimizing resume: {str(e)}")
            raise

    async def generate_resume_pdf(self, resume_data: Dict[str, Any], personal_info: Dict[str, Any], 
                                job_title: str, job_description: str) -> str:
        """
        Generate a PDF resume using LaTeX.
        
        Args:
            resume_data: Dictionary containing resume sections (summary, experience, etc.)
            personal_info: Dictionary containing personal information (name, email, etc.)
            job_title: The title of the job being applied for
            job_description: The job description text
            
        Returns:
            str: Path to the generated PDF file
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
            return pdf_path

        except Exception as e:
            logger.error(f"Error generating PDF resume: {str(e)}")
            raise
