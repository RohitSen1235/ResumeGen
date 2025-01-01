import os
import subprocess
import tempfile
import json
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

    def escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters in text."""
        if not text:
            return ""
        # List of special LaTeX characters that need escaping
        special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            # '~': r'\textasciitilde{}',
            # '^': r'\textasciicircum{}',
            # '\\': r'\textbackslash{}',
            # '<': r'\textless{}',
            # '>': r'\textgreater{}',
        }
        # Escape each special character
        for char, escape_seq in special_chars.items():
            text = text.replace(char, escape_seq)
        return text

    def validate_and_clean(self, data: dict) -> dict:
        """Validate and clean resume data."""
        cleaned = {}
        
        # Required fields
        cleaned['name'] = self.escape_latex(data.get('name', 'Your Name'))
        cleaned['email'] = self.escape_latex(data.get('email', 'email@example.com'))
        
        # Optional fields with defaults
        cleaned['phone'] = self.escape_latex(data.get('phone', ''))
        cleaned['location'] = self.escape_latex(data.get('location', ''))
        cleaned['linkedin'] = self.escape_latex(data.get('linkedin', ''))
        cleaned['job_title'] = self.escape_latex(data.get('job_title', 'Your Job Title'))
        
        # Sections with defaults
        cleaned['summary'] = self.escape_latex(data.get('summary', ''))
        
        # Skills
        cleaned['skills'] = [self.escape_latex(skill) for skill in data.get('skills', [])]
        
        # Experience
        cleaned['experience'] = []
        for exp in data.get('experience', []):
            cleaned_exp = {
                'title': self.escape_latex(exp.get('title', 'Position Title')),
                'company': self.escape_latex(exp.get('company', 'Company Name')),
                'duration': self.escape_latex(exp.get('duration', 'Dates')),
                'achievements': [self.escape_latex(ach) for ach in exp.get('achievements', [])]
            }
            cleaned['experience'].append(cleaned_exp)
        
        # Education
        cleaned['education'] = []
        for edu in data.get('education', []):
            cleaned_edu = {
                'degree': self.escape_latex(edu.get('degree', 'Degree')),
                'institution': self.escape_latex(edu.get('institution', 'Institution')),
                'year': self.escape_latex(edu.get('year', 'Year'))
            }
            cleaned['education'].append(cleaned_edu)
        
        # Certifications
        cleaned['certifications'] = [self.escape_latex(cert) for cert in data.get('certifications', [])]
        
        return cleaned

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
        logger.info(f"Parsing experience text:\n{experience_text}")
        experiences = []
        current_exp = None
        current_achievements = []

        for line in experience_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Handle both bullet point formats
            if line.startswith('•') or line.startswith('-'):
                # This is an achievement
                achievement = line[1:].strip()
                if achievement:
                    current_achievements.append(achievement)
            else:
                # If we have a previous experience, save it
                if current_exp:
                    current_exp['achievements'] = current_achievements
                    experiences.append(current_exp)
                    current_achievements = []

                # This is a new experience entry
                # Handle bold formatting in job titles
                line = line.replace('**', '')
                if ',' in line:
                    parts = line.split(',', 2)
                    if len(parts) >= 2:
                        title = parts[0].strip()
                        company = parts[1].strip() if len(parts) > 2 else ''
                        duration = parts[-1].strip()

                        current_exp = {
                            'title': title,
                            'company': company,
                            'duration': duration,
                            'achievements': []
                        }

        # Add the last experience, if it exists
        if current_exp:
            current_exp['achievements'] = current_achievements
            experiences.append(current_exp)

        return experiences

    def parse_education(self, education_text: str) -> list:
        """Parse education section into structured format."""
        education = []
        lines = [line.strip() for line in education_text.split('\n') if line.strip()]
        
        # Process education entries that may span multiple lines
        current_entry = {}
        for line in lines:
            if not current_entry:
                current_entry['degree'] = line
            elif 'institution' not in current_entry:
                current_entry['institution'] = line
            else:
                current_entry['year'] = line
                education.append(current_entry)
                current_entry = {}

        return education

    def parse_skills(self, skills_text: str) -> list:
        """Parse skills section into list."""
        skills = []
        current_skill = ""
        
        for line in skills_text.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                if current_skill:
                    skills.append(current_skill.strip())
                current_skill = line[1:].strip()
            elif current_skill:
                # Handle multi-line skills
                current_skill += " " + line.strip()
        
        if current_skill:
            skills.append(current_skill.strip())
            
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
            logger.info(f"Parsing AI content:\n{ai_content}")
            sections = self.parse_ai_content(ai_content)
            logger.info(f"Parsed sections: {list(sections.keys())}")
            logger.info(f"Professional Experience section: {sections.get('Professional Experience', 'Not found')}")

            # Create initial content structure
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

            # Clean and validate the content
            cleaned_content = self.validate_and_clean(formatted_content)

            logger.info(f"Final formatted content:\n{json.dumps(cleaned_content, indent=2)}")
            return cleaned_content

        except Exception as e:
            logger.error(f"Error formatting content: {str(e)}")
            raise

    def format_report_data(self, agent_outputs: str, total_usage: dict) -> dict:
        """Format report data for LaTeX template."""
        try:
            # Extract scores from agent outputs
            scores = {
                'content_quality_score': float(agent_outputs.split("quality score")[1].split(":")[1].split()[0]),
                'skills_match_score': float(agent_outputs.split("match score")[1].split(":")[1].split()[0]),
                'experience_quality_score': float(agent_outputs.split("quality score")[1].split(":")[1].split()[0])
            }
            
            # Extract analysis sections
            analysis = {
                'content_quality_analysis': agent_outputs.split("Content Quality Analysis:")[1].split("####")[0].strip(),
                'skills_analysis': agent_outputs.split("Skills Analysis:")[1].split("####")[0].strip(),
                'experience_analysis': agent_outputs.split("Experience Analysis:")[1].split("####")[0].strip()
            }
            
            # Format usage statistics
            usage = {
                'total_input_tokens': total_usage['total_input_tokens'],
                'total_output_tokens': total_usage['total_output_tokens'],
                'total_cost': round(total_usage['total_cost'], 2)
            }
            
            return {**scores, **analysis, **usage}
            
        except Exception as e:
            logger.error(f"Error formatting report data: {str(e)}")
            raise

    def generate_report_pdf(self, template_name: str, data: dict) -> str:
        """Generate PDF from specified template and data."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate LaTeX content
                template = self.env.get_template(template_name)
                latex_content = template.render(**data)

                # Write LaTeX file
                tex_path = os.path.join(temp_dir, 'output.tex')
                with open(tex_path, 'w') as f:
                    f.write(latex_content)

                # Compile LaTeX to PDF
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    # Verify required packages are installed
                    package_check = subprocess.run(
                        ['kpsewhich', 'fontawesome5.sty', 'lmodern.sty', 'hyperref.sty',
                         'geometry.sty', 'titlesec.sty', 'fancyhdr.sty', 'ragged2e.sty'],
                        capture_output=True,
                        text=True
                    )
                    
                    if package_check.returncode != 0:
                        missing_packages = [pkg for pkg in package_check.stdout.split('\n') if not pkg]
                        if missing_packages:
                            raise Exception(f"Missing LaTeX packages: {', '.join(missing_packages)}")

                    # Run pdflatex twice to resolve references
                    for i in range(2):
                        process = subprocess.run(
                            ['pdflatex', '-interaction=nonstopmode', 'output.tex'],
                            capture_output=True,
                            text=True
                        )
                        
                        # Write full LaTeX output to log file for debugging
                        log_path = os.path.join(temp_dir, f'latex_output_{i}.log')
                        with open(log_path, 'w') as log_file:
                            log_file.write(f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}")
                        
                        if process.returncode != 0:
                            error_output = process.stderr if process.stderr else process.stdout
                            logger.error(f"PDF compilation failed with output:\n{error_output}")
                            logger.error(f"Full LaTeX output:\n{process.stdout}")
                            # Include the log file path in the error message
                            raise Exception(f"PDF compilation failed: {error_output}\nSee full log at: {log_path}")

                    # Check if PDF was created
                    pdf_path = os.path.join(temp_dir, 'output.pdf')
                    if not os.path.exists(pdf_path):
                        raise Exception("PDF file was not created")

                    # Create output directory if it doesn't exist
                    output_dir = Path(__file__).parent.parent / "output"
                    output_dir.mkdir(exist_ok=True)

                    # Generate unique filename
                    timestamp = int(time.time())
                    output_filename = f"{template_name.split('.')[0]}_{timestamp}.pdf"
                    output_path = output_dir / output_filename

                    # Copy PDF to output directory
                    with open(pdf_path, 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())

                    logger.info(f"Successfully generated PDF at: {output_path}")
                    return str(output_path)

                finally:
                    os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
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
                    # Verify required packages are installed
                    package_check = subprocess.run(
                        ['kpsewhich', 'fontawesome5.sty', 'lmodern.sty', 'hyperref.sty',
                         'geometry.sty', 'titlesec.sty', 'fancyhdr.sty', 'ragged2e.sty'],
                        capture_output=True,
                        text=True
                    )
                    
                    if package_check.returncode != 0:
                        missing_packages = [pkg for pkg in package_check.stdout.split('\n') if not pkg]
                        if missing_packages:
                            raise Exception(f"Missing LaTeX packages: {', '.join(missing_packages)}")

                    # Run pdflatex twice to resolve references
                    for i in range(2):
                        process = subprocess.run(
                            ['pdflatex', '-interaction=nonstopmode', 'resume.tex'],
                            capture_output=True,
                            text=True
                        )
                        
                        # Write full LaTeX output to log file for debugging
                        log_path = os.path.join(temp_dir, f'latex_output_{i}.log')
                        with open(log_path, 'w') as log_file:
                            log_file.write(f"STDOUT:\n{process.stdout}\n\nSTDERR:\n{process.stderr}")
                        
                        if process.returncode != 0:
                            error_output = process.stderr if process.stderr else process.stdout
                            logger.error(f"PDF compilation failed with output:\n{error_output}")
                            logger.error(f"Full LaTeX output:\n{process.stdout}")
                            # Include the log file path in the error message
                            raise Exception(f"PDF compilation failed: {error_output}\nSee full log at: {log_path}")

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
