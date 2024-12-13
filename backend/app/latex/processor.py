import os
import subprocess
import tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfWriter, PdfReader
import logging
import re

logger = logging.getLogger(__name__)

class LatexProcessor:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]',
            trim_blocks=True,
            autoescape=False,
        )

    def parse_ai_content(self, content: str) -> dict:
        """
        Parse AI-generated content into structured sections.
        The content follows this format:
        # Section Name
        ===
        content
        ===
        """
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            line = line.rstrip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for section header
            if line.startswith('# '):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = line[2:].strip()  # Remove '# ' prefix
                current_content = []
                continue
                
            # Skip section markers
            if line == '===':
                continue
                
            # Add content line
            if current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
            
        return sections

    def parse_experience(self, experience_text: str) -> list:
        """Parse experience section into structured format."""
        experiences = []
        current_exp = None
        current_achievements = []

        for line in experience_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('•'):
                # This is an achievement
                achievement = line[1:].strip()
                current_achievements.append(achievement)
            else:
                # If we have a previous experience, save it
                if current_exp and current_achievements:
                    current_exp['achievements'] = current_achievements
                    experiences.append(current_exp)
                    current_achievements = []

                # This is a new experience entry
                if ',' in line:
                    parts = line.split(',', 1)
                    title_company = parts[0].strip()
                    duration = parts[1].strip()

                    # Split title and company
                    if ' at ' in title_company:
                        title, company = title_company.split(' at ', 1)
                    else:
                        title = title_company
                        company = ''

                    current_exp = {
                        'title': title.strip(),
                        'company': company.strip(),
                        'duration': duration.strip()
                    }

        # Add the last experience
        if current_exp and current_achievements:
            current_exp['achievements'] = current_achievements
            experiences.append(current_exp)

        return experiences

    def parse_education(self, education_text: str) -> list:
        """Parse education section into structured format."""
        education = []
        lines = [line.strip() for line in education_text.split('\n') if line.strip()]
        
        for i in range(0, len(lines), 3):  # Process 3 lines at a time
            if i + 2 < len(lines):
                edu_entry = {
                    'degree': lines[i],
                    'institution': lines[i + 1],
                    'year': lines[i + 2]
                }
                education.append(edu_entry)

        return education

    def parse_skills(self, skills_text: str) -> list:
        """Parse skills section into list."""
        skills = []
        for line in skills_text.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                skill = line[1:].strip()
                if skill:
                    skills.append(skill)
        return skills

    def parse_certifications(self, certifications_text: str) -> list:
        """Parse certifications section into list."""
        certifications = []
        for line in certifications_text.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                cert = line[1:].strip()
                if cert and cert.lower() != 'none':
                    certifications.append(cert)
        return certifications

    def format_content(self, personal_info: dict, ai_content: str, job_title: str) -> dict:
        """Format content for LaTeX template."""
        try:
            # Validate required personal info
            if not personal_info.get('name'):
                raise ValueError("Name is required in personal information")
            if not personal_info.get('email'):
                raise ValueError("Email is required in personal information")

            # Parse AI-generated content
            sections = self.parse_ai_content(ai_content)

            # Create formatted content structure
            formatted_content = {
                # Personal Information
                "name": personal_info['name'],
                "email": personal_info['email'],
                "phone": personal_info.get('phone', ''),
                "location": personal_info.get('location', ''),
                "linkedin": personal_info.get('linkedin', ''),
                "job_title": job_title,
                
                # Professional Summary
                "summary": sections.get('Professional Summary', ''),
                
                # Skills
                "skills": self.parse_skills(sections.get('Key Skills', '')),
                
                # Experience
                "experience": self.parse_experience(sections.get('Professional Experience', '')),
                
                # Education
                "education": self.parse_education(sections.get('Education', '')),
                
                # Certifications
                "certifications": self.parse_certifications(sections.get('Certifications', ''))
            }

            return formatted_content

        except Exception as e:
            logger.error(f"Error formatting content: {str(e)}")
            raise

    def generate_resume_pdf(self, content: dict) -> str:
        """Generate PDF resume from formatted content."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate LaTeX content
                template = self.env.get_template('resume.tex.j2')
                latex_content = template.render(**content)

                # Write LaTeX file
                tex_path = os.path.join(temp_dir, 'resume.tex')
                with open(tex_path, 'w') as f:
                    f.write(latex_content)

                # Compile LaTeX to PDF
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    # Run pdflatex twice to resolve references
                    for _ in range(2):
                        process = subprocess.run(
                            ['pdflatex', '-interaction=nonstopmode', 'resume.tex'],
                            capture_output=True,
                            text=True
                        )
                        
                        if process.returncode != 0:
                            raise Exception("PDF compilation failed")

                    # Check if PDF was created
                    pdf_path = os.path.join(temp_dir, 'resume.pdf')
                    if not os.path.exists(pdf_path):
                        raise Exception("PDF file was not created")

                    # Create output directory if it doesn't exist
                    output_dir = Path(__file__).parent.parent / "output"
                    output_dir.mkdir(exist_ok=True)

                    # Copy PDF to output directory
                    output_path = output_dir / f"resume_{content.get('job_title', 'generated')}.pdf"
                    with open(pdf_path, 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())

                    logger.info(f"Successfully generated PDF resume at: {output_path}")
                    return str(output_path)

                finally:
                    os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
