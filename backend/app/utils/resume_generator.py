import groq
import os
import time
import logging
from typing import Dict, Any, List, Tuple, Optional
import json
from pathlib import Path
from ..latex.processor import LatexProcessor
import tiktoken
import subprocess
from .resume_assessment_agents import (
                content_quality_agent,
                # formatting_agent,
                skills_agent,
                experience_agent,
                resume_constructor_agent,
                content_quality_task,
                # formatting_task,
                skills_task,
                experience_task,
                resume_construction_task,
                calculate_total_tokens
            )


logger = logging.getLogger(__name__)

class TokenTracker:
    """Tracks token usage and calculates costs for Groq API calls"""
    
    COST_PER_MILLION_TOKENS = 40  # $20 per million tokens
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.agent_input_tokens = 0
        self.agent_output_tokens = 0
        self.session_history = []
        self.agent_history = []
        self.encoder = tiktoken.get_encoding("cl100k_base")  # Using OpenAI's tokenizer as approximation
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in a string using the tokenizer"""
        return len(self.encoder.encode(text))
    
    def add_api_call(self, prompt: str, response: str) -> Dict[str, Any]:
        """Record a new API call with input and output tokens"""
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(response)
        
        self.total_input_tokens += input_tokens * 2
        self.total_output_tokens += output_tokens * 2
        
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
        return (num_tokens / 1_000_000) * self.COST_PER_MILLION_TOKENS * 90
    
    def add_agent_call(self, agent_name: str, context: str, response: str) -> Dict[str, Any]:
        """Record a new agent call with input and output tokens"""
        input_tokens = self.count_tokens(context)
        output_tokens = self.count_tokens(response)
        
        self.agent_input_tokens += input_tokens
        self.agent_output_tokens += output_tokens
        
        call_stats = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'agent': agent_name,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': self.calculate_cost(input_tokens),
            'output_cost': self.calculate_cost(output_tokens),
            'total_cost': self.calculate_cost(input_tokens + output_tokens)
        }
        
        self.agent_history.append(call_stats)
        return call_stats

    def get_total_usage(self) -> Dict[str, Any]:
        """Get total token usage and costs for all API calls and agent calls"""
        total_input_tokens = self.total_input_tokens + self.agent_input_tokens
        total_output_tokens = self.total_output_tokens + self.agent_output_tokens
        total_tokens = total_input_tokens + total_output_tokens
        
        return {
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'agent_input_tokens': self.agent_input_tokens,
            'agent_output_tokens': self.agent_output_tokens,
            'total_tokens': total_tokens,
            'total_input_cost': self.calculate_cost(total_input_tokens),
            'total_output_cost': self.calculate_cost(total_output_tokens),
            'total_cost': self.calculate_cost(total_tokens),
            'call_history': self.session_history,
            'agent_history': self.agent_history
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
            List 4-6 most relevant skills, each on a new line starting with •
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

            # Projects
            ===
            List relevant projects, each on a new line starting with •
            Format each project as:
            • [Project Title] - [Brief Description]
            Technologies: [List of technologies used]

            Example:
            • E-commerce Platform - Built a scalable online marketplace
            Technologies: React, Node.js, MongoDB
            ===

            # Others
            ===
            List any other relevant information, each on a new line starting with •
            Example:
            • Open source contributions
            • Professional memberships
            • Awards and recognitions
            ===

            Important:
            1. Keep the exact section headers (# Section Name)
            2. Keep the === markers before and after each section's content
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

    def get_existing_resume(self, user_id: int) -> Optional[str]:
        """
        Check if user has an existing resume in uploads directory.
        Returns the parsed text content if found, None otherwise.
        """
        from .resume_parser import parse_resume
        
        # Use absolute path for Docker container
        # Use absolute path for Docker container
        uploads_dir = Path("/app/uploads")
        resume_pattern = f"resume_{user_id}_*.pdf"
        
        try:
            # Find matching resume files
            matching_resumes = list(uploads_dir.glob(resume_pattern))
            logger.info(f"Searching for resumes in {uploads_dir} with pattern {resume_pattern}")
            logger.info(f"Found {len(matching_resumes)} matching resumes")
            
            if not matching_resumes:
                logger.info(f"No existing resumes found for user {user_id}")
                return None
                
            # Get most recent resume
            latest_resume = max(matching_resumes, key=lambda p: p.stat().st_mtime)
            
            # Parse and return resume text content
            return parse_resume(str(latest_resume))
            
        except Exception as e:
            logger.error(f"Error accessing resume files: {str(e)}")
            return None

    async def optimize_resume(self, professional_info: Dict[str, Any], job_description: str, skills: Optional[List[str]] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Main function to optimize the entire resume using and assessment agents.
        Returns the optimized content along with token usage statistics.
        """
        try:
            # Check for existing resume first
            initial_content = None
            usage_stats = {}
            
            if user_id is not None:
                existing_resume = self.get_existing_resume(user_id)
                if existing_resume is not None:
                    initial_content = existing_resume
                    logger.info(f"Used Existing Resume")
            # Generate initial content using Groq AI if no existing resume
            if initial_content is None:
                initial_content, usage_stats = self.generate_optimized_resume(professional_info, job_description, skills)
                logger.info(f"Used Fake Resume from Groq")
            
            context:str = f"job description:\n{job_description}\n############\ninitial_content:\n{initial_content}"
            # Process content through assessment agents
            # content_quality_task.context = [initial_content,job_description]
            # formatting_task.context = [initial_content,job_description]
            # skills_task.context = [initial_content,job_description]
            # experience_task.context = [initial_content,job_description]
            
            # Execute tasks sequentially
            # Execute tasks and track token usage
            content_quality_result = content_quality_agent.execute_task(content_quality_task,context=context)
            self.token_tracker.add_agent_call(
                "content_quality_agent",
                context,
                content_quality_result
            )
            
            # formatting_result = formatting_agent.execute_task(formatting_task,context=context)
            
            skills_result = skills_agent.execute_task(skills_task,context=context)
            self.token_tracker.add_agent_call(
                "skills_agent",
                context,
                skills_result
            )
            
            experience_result = experience_agent.execute_task(experience_task, context=context)
            self.token_tracker.add_agent_call(
                "experience_agent",
                context,
                experience_result
            )
            
            # Combine initial agent outputs
            agent_outputs = f"""
            {content_quality_result}
            \n
            {skills_result}
            \n
            {experience_result}
            """
            final_context = f"job description:\n{job_description}\n############\nExpert Suggestions:\n{agent_outputs}"

            # print(f"Agent Output :\n###{agent_outputs}###")
            # Construct final resume using construction agent
            final_resume = resume_constructor_agent.execute_task(resume_construction_task,context=agent_outputs)

            return {
                'ai_content': final_resume,
                'professional_info': professional_info,
                'token_usage': usage_stats,
                'total_usage': self.token_tracker.get_total_usage(),
                'agent_outputs': agent_outputs
            }

        except Exception as e:
            logger.error(f"Error optimizing resume: {str(e)}")
            raise

    def _extract_scores(self, agent_output: str) -> Dict[str, float]:
        """Extract scores from agent output text"""
        scores = {}
        if "quality score" in agent_output:
            scores['content_quality'] = float(agent_output.split("quality score")[1].split(":")[1].split()[0])
        if "match score" in agent_output:
            scores['skills_match'] = float(agent_output.split("match score")[1].split(":")[1].split()[0])
        if "quality score" in agent_output:
            scores['experience_quality'] = float(agent_output.split("quality score")[1].split(":")[1].split()[0])
        return scores

    def _format_report_data(self, agent_outputs: str, total_usage: Dict[str, Any]) -> Dict[str, Any]:
        """Format agent outputs and usage stats for report template"""
        scores = self._extract_scores(agent_outputs)
        return {
            'content_quality_score': scores.get('content_quality', 0),
            'skills_match_score': scores.get('skills_match', 0),
            'experience_quality_score': scores.get('experience_quality', 0),
            'content_quality_analysis': agent_outputs.split("Content Quality Analysis:")[1].split("####")[0].strip(),
            'skills_analysis': agent_outputs.split("Skills Analysis:")[1].split("####")[0].strip(),
            'experience_analysis': agent_outputs.split("Experience Analysis:")[1].split("####")[0].strip(),
            'total_input_tokens': total_usage['total_input_tokens'],
            'total_output_tokens': total_usage['total_output_tokens'],
            'total_cost': round(total_usage['total_cost'], 2)
        }

    async def generate_report_pdf(self, agent_outputs: str, total_usage: Dict[str, Any]) -> str:
        """Generate a PDF report from agent outputs"""
        try:
            # Format the report data using the processor
            formatted_data = self.latex_processor.format_report_data(agent_outputs, total_usage)
            
            # Generate the PDF using the formatted data
            pdf_path = self.latex_processor.generate_pdf(
                template_name='report.tex.j2',
                data=formatted_data
            )
            logger.info(f"Successfully generated report PDF at: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error generating report PDF: {str(e)}")
            raise

    def _generate_docx(self, content: str, output_path: str) -> str:
        """Generate DOCX document using python-docx"""
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
            
            # Create a new document
            doc = Document()
            
            # Set default styles
            style = doc.styles['Normal']
            font = style.font
            font.name = 'Calibri'
            font.size = Pt(11)
            
            # Add content sections
            sections = content.split('#')
            for section in sections:
                if not section.strip():
                    continue
                    
                # Split section into title and content
                section_parts = section.split('\n', 1)
                title = section_parts[0].strip()
                body = section_parts[1].strip() if len(section_parts) > 1 else ''
                
                # Add section title
                heading = doc.add_heading(title, level=1)
                heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                
                # Add section content
                if body:
                    for line in body.split('\n'):
                        if line.strip():
                            p = doc.add_paragraph(line.strip())
                            p.style = doc.styles['Normal']
            
            # Save the document
            doc.save(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating DOCX: {str(e)}")
            raise RuntimeError(f"Failed to generate DOCX: {str(e)}")

    async def generate_resume_docx(self, resume_data: Dict[str, Any], personal_info: Dict[str, Any],
                                 job_title: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate a Word document resume using python-docx.
        Returns both the DOCX path and token usage statistics.
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(__file__).parent.parent / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = int(time.time())
            docx_path = str(output_dir / f"resume_{timestamp}.docx")
            
            # Format the content
            content = self._format_docx_content(resume_data, personal_info, job_title)
            
            # Generate DOCX
            self._generate_docx(content, docx_path)
            
            # Get the total token usage statistics
            total_usage = self.token_tracker.get_total_usage()
            
            logger.info(f"Successfully generated DOCX resume at: {docx_path}")
            return docx_path, total_usage

        except Exception as e:
            logger.error(f"Error generating DOCX resume: {str(e)}")
            raise

    def _format_docx_content(self, resume_data: Dict[str, Any], personal_info: Dict[str, Any],
                           job_title: str) -> str:
        """Format resume content for DOCX generation"""
        content = f"""
# {personal_info.get('name', 'Resume')}
{personal_info.get('email', '')} | {personal_info.get('phone', '')}
{personal_info.get('location', '')} | {personal_info.get('linkedin', '')}

# Professional Summary
{resume_data['ai_content'].split('# Professional Summary')[1].split('#')[0].strip()}

# Skills
{resume_data['ai_content'].split('# Skills')[1].split('#')[0].strip()}

# Experience
{resume_data['ai_content'].split('# Experience')[1].split('#')[0].strip()}

# Education
{resume_data['ai_content'].split('# Education')[1].split('#')[0].strip()}

# Projects
{resume_data['ai_content'].split('# Projects')[1].split('#')[0].strip() if '# Projects' in resume_data['ai_content'] else ''}

# Others
{resume_data['ai_content'].split('# Others')[1].split('#')[0].strip() if '# Others' in resume_data['ai_content'] else ''}
"""
        return content.strip()

    async def generate_resume(self, resume_data: Dict[str, Any], personal_info: Dict[str, Any],
                            job_title: str, format: str = 'pdf') -> Tuple[str, Dict[str, Any]]:
        """
        Generate a resume in the specified format (pdf or docx).
        Returns both the file path and token usage statistics.
        """
        if format.lower() == 'docx':
            return await self.generate_resume_docx(resume_data, personal_info, job_title)
        
        # Format the content for the LaTeX template
        try:
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
