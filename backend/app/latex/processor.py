import os
import subprocess
import tempfile
import json
import uuid
from pathlib import Path
import time
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, BaseLoader, TemplateNotFound
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfWriter, PdfReader
import logging
import re
from sqlalchemy.orm import Session
from .. import models
from ..utils.s3_storage import s3_storage

logger = logging.getLogger(__name__)

class S3TemplateLoader(BaseLoader):
    def __init__(self):
        pass

    def get_source(self, environment, template):
        content = s3_storage.download_text(template)
        if content is None:
            raise TemplateNotFound(template)
        return content, template, lambda: True

class LatexProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.env = Environment(
            loader=S3TemplateLoader(),
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]',
            trim_blocks=True,
            autoescape=False,
        )
        self._load_templates()

    def _load_templates(self):
        """Load templates from the database."""
        try:
            self.templates = self.db.query(models.LatexTemplate).filter(models.LatexTemplate.is_active == True).all()
            logger.info(f"Loaded {len(self.templates)} templates from the database")
        except Exception as e:
            logger.error(f"Error loading templates from database: {str(e)}")
            self.templates = []
            raise ValueError("Failed to load templates from the database")

    def get_available_templates(self) -> list:
        """Return list of available templates."""
        return [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "file_path": t.file_path,
                "image_path": s3_storage.generate_presigned_url(t.image_path) if t.image_path else None,
                "is_default": t.is_default,
                "single_page": t.single_page,
                "is_active": t.is_active,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
            }
            for t in self.templates
        ]

    def get_all_template_contents(self) -> list:
        """Return list of available templates with their content."""
        templates_with_content = []
        for t in self.templates:
            try:
                content = s3_storage.download_text(t.file_path)
                if content:
                    templates_with_content.append({
                        "name": t.name,
                        "content": content
                    })
            except Exception as e:
                logger.warning(f"Could not load content for template {t.name}: {str(e)}")
        return templates_with_content

    def get_template_info(self, template_id: str) -> models.LatexTemplate:
        """Get template metadata by ID."""
        for template in self.templates:
            if str(template.id) == template_id:
                return template
        raise ValueError(f"Template not found: {template_id}")

    def validate_template(self, template_id: str) -> bool:
        """Validate that template exists and is properly configured."""
        self.get_template_info(template_id)
        return True

    def get_default_template_id(self) -> str:
        """Get the ID of the default template from the database."""
        try:
            default_template = self.db.query(models.LatexTemplate).filter(models.LatexTemplate.is_default == True, models.LatexTemplate.is_active == True).first()
            if default_template:
                return str(default_template.id)
            # Fallback to the first active template if no default is set
            first_template = self.db.query(models.LatexTemplate).filter(models.LatexTemplate.is_active == True).first()
            if first_template:
                return str(first_template.id)
            raise ValueError("No active templates found in the database")
        except Exception as e:
            logger.error(f"Error getting default template: {str(e)}")
            raise ValueError("Could not determine default template")

    def escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters in text."""
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # List of special LaTeX characters that need escaping
        # Order matters - do backslash first to avoid double escaping
        special_chars = [
            ('\\', r'\textbackslash{}'),  # Handle backslash first
            ('&', r'\&'),
            ('%', r'\%'),
            ('$', r'\$'),
            ('#', r'\#'),
            ('_', r'\_'),
            ('{', r'\{'),
            ('}', r'\}'),
            ('^', r'\textasciicircum{}'),
            ('~', r'\textasciitilde{}'),
            ('<', r'\textless{}'),
            ('>', r'\textgreater{}'),
            ('|', r'\textbar{}'),
            ('`', r'\textasciigrave{}'),
            ("'", r'\textquotesingle{}'),
            ('"', r'\textquotedbl{}'),
            ('©', r'\textcopyright{}'),
            ('®', r'\textregistered{}'),
            ('™', r'\texttrademark{}'),
            ('£', r'\pounds{}'),
            ('€', r'\euro{}'),
            ('¥', r'\yen{}'),
            ('§', r'\S{}'),
            ('¶', r'\P{}'),
        ]
        
        # Escape each special character
        for char, escape_seq in special_chars:
            text = text.replace(char, escape_seq)
        
        # Handle line breaks in LaTeX
        text = text.replace('\n', '\\\\')
        
        # Handle multiple consecutive spaces
        text = re.sub(r' {2,}', ' ', text)
        
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
        
        # Achievements
        cleaned['achievements'] = [self.escape_latex(ach) for ach in data.get('achievements', [])]
        
        # Projects
        cleaned['projects'] = []
        for proj in data.get('projects', []):
            cleaned_proj = {
                'title': self.escape_latex(proj.get('title', '')),
                'highlights': [self.escape_latex(highlight) for highlight in proj.get('highlights', [])]
            }
            cleaned['projects'].append(cleaned_proj)
        
        # Others
        cleaned['others'] = [self.escape_latex(other) for other in data.get('others', [])]
        
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
        
        # Handle multiple formats:
        # 1. Single line format: "Degree | Institution | Year"
        # 2. Multi-line format with bullet points
        # 3. Multi-line format without bullet points
        
        current_entry = {}
        for line in lines:
            if line.startswith('•'):
                line = line[1:].strip()
            
            if '|' in line:
                # Single line format
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    education.append({
                        'degree': parts[0],
                        'institution': parts[1],
                        'year': parts[2]
                    })
                elif len(parts) == 2:
                    education.append({
                        'degree': parts[0],
                        'institution': parts[1],
                        'year': ''
                    })
                else:
                    education.append({
                        'degree': parts[0],
                        'institution': '',
                        'year': ''
                    })
            else:
                # Multi-line format
                if not current_entry:
                    current_entry = {'degree': line}
                elif 'institution' not in current_entry:
                    current_entry['institution'] = line
                else:
                    current_entry['year'] = line
                    education.append(current_entry)
                    current_entry = {}

        # Add last entry if exists
        if current_entry:
            education.append(current_entry)

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
            if not line or line.lower() == 'none':
                continue
                
            # Handle both bullet point and plain text formats
            if line.startswith('•'):
                line = line[1:].strip()
            certifications.append(line)
        return certifications

    def parse_achievements(self, achievements_text: str) -> list:
        """Parse achievements section into list."""
        achievements = []
        for line in achievements_text.split('\n'):
            line = line.strip()
            if not line or line.lower() == 'none':
                continue
                
            # Handle both bullet point and plain text formats
            if line.startswith('•'):
                line = line[1:].strip()
            achievements.append(line)
        return achievements

    def parse_projects(self, projects_text: str) -> list:
        """Parse projects section into structured format."""
        projects = []
        current_project = None
        current_highlights = []
        
        lines = projects_text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
                
            # If line doesn't start with bullet point and isn't empty,
            # it's likely a project title
            if not line.startswith('•') and line:
                # Save previous project if exists
                if current_project and current_highlights:
                    current_project['highlights'] = current_highlights
                    projects.append(current_project)
                
                # Start new project
                current_project = {'title': line.strip('*'), 'highlights': []}
                current_highlights = []
                
            # If line starts with bullet point, it's a highlight
            elif line.startswith('•'):
                if current_project:
                    current_highlights.append(line[1:].strip())
                    
            i += 1
        
        # Add the last project
        if current_project and current_highlights:
            current_project['highlights'] = current_highlights
            projects.append(current_project)
            
        return projects

    def parse_others(self, others_text: str) -> list:
        """Parse others section into list."""
        others = []
        for line in others_text.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                item = line[1:].strip()
                if item and item.lower() != 'none':
                    others.append(item)
        return others

    def format_content(self, personal_info: dict, ai_content: str, job_title: str, template_id: str = None) -> dict:
        """Format content for LaTeX template."""
        try:
            # Validate required personal info
            if not personal_info.get('name'):
                raise ValueError("Name is required in personal information")
            if not personal_info.get('email'):
                raise ValueError("Email is required in personal information")

            # Check if template is single-page
            is_single_page = False
            if template_id:
                try:
                    template_info = self.get_template_info(template_id)
                    is_single_page = template_info.single_page
                except ValueError:
                    # logger.error(f"template_id parameter : {template_id} is not valid")
                    raise ValueError(f"template_id parameter : {template_id} is not valid")

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
                "certifications": self.parse_certifications(sections.get('Certifications', '')),
                
                # Achievements
                "achievements": self.parse_achievements(sections.get('Achievements', '')),
                
                # Projects
                "projects": self.parse_projects(sections.get('Projects', '')),
                
                # Others
                "others": self.parse_others(sections.get('Others', ''))
            }

            # Clean and validate the content
            cleaned_content = self.validate_and_clean(formatted_content)

            # Limit items for single-page templates
            if is_single_page:
                if len(cleaned_content.get('experience', [])) > 3:
                    cleaned_content['experience'] = cleaned_content['experience'][:3]
                    logger.info("Limited experience items to 3 for single-page template")
                
                if len(cleaned_content.get('projects', [])) > 3:
                    cleaned_content['projects'] = cleaned_content['projects'][:3]
                    logger.info("Limited project items to 3 for single-page template")

            # Debug log to verify achievements and certifications are included
            logger.info("Verifying achievements and certifications in formatted content:")
            logger.info(f"Experience entries: {len(cleaned_content.get('experience', []))}")
            for exp in cleaned_content.get('experience', []):
                logger.info(f"Experience at {exp.get('company')} has {len(exp.get('achievements', []))} achievements")
            logger.info(f"Certifications: {len(cleaned_content.get('certifications', []))}")
            
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

    async def generate_template_from_image(
        self,
        image_file,
        template_name: str = "AI Generated Template",
        template_description: str = "Generated from uploaded design",
        current_user=None
    ) -> Dict[str, Any]:
        """
        Generate LaTeX template from uploaded design image using AI.
        Stores result in AIGeneratedTemplate table for admin review.

        Args:
            image_file: Uploaded image file (UploadFile)
            template_name: Name for the generated template
            template_description: Description for the generated template
            current_user: Current admin user (for tracking)

        Returns:
            Dict containing:
            - ai_template: Stored template metadata
            - latex_code: Generated LaTeX template code
            - test_data: Sample data for testing
            - validation: Compilation validation results
            - metadata: Template metadata
            - image_analysis: AI analysis of the source image
        """
        try:
            logger.info(f"Starting AI template generation for: {template_name}")

            # Import here to avoid circular dependency
            from ..utils.ai_template_generator import AITemplateGenerator

            # Initialize AI template generator
            ai_generator = AITemplateGenerator(self.db)

            # Generate template from image
            result = await ai_generator.generate_template_from_image(
                image_file=image_file,
                template_name=template_name,
                template_description=template_description,
                current_user=current_user
            )

            logger.info(f"Successfully created AI-generated template: {template_name}")

            return result

        except Exception as e:
            logger.error(f"Error generating template from image: {str(e)}")
            raise

    def _compile_latex_to_pdf(self, tex_path: str) -> str:
        """
        Compile LaTeX file to PDF using xelatex.
        This is a helper method used by the validation process.
        """
        try:
            # Get directory and filename
            tex_dir = os.path.dirname(tex_path)
            tex_filename = os.path.basename(tex_path)
            pdf_filename = tex_filename.replace('.tex', '.pdf')

            # Change to the LaTeX file directory
            original_dir = os.getcwd()
            os.chdir(tex_dir)

            try:
                # Run xelatex twice to resolve references
                for i in range(2):
                    process = subprocess.run(
                        ['xelatex', '-interaction=nonstopmode', tex_filename],
                        capture_output=True,
                        text=True
                    )

                    if process.returncode != 0:
                        error_output = process.stderr if process.stderr else process.stdout
                        logger.error(f"LaTeX compilation failed: {error_output}")
                        raise Exception(f"LaTeX compilation failed: {error_output}")

                # Check if PDF was created
                pdf_path = os.path.join(tex_dir, pdf_filename)
                if not os.path.exists(pdf_path):
                    raise Exception("PDF file was not created")

                return pdf_path

            finally:
                os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error compiling LaTeX to PDF: {str(e)}")
            raise

    # important
    def generate_resume_pdf(self, content: dict, template_id: str = None, user_id: str = None) -> dict:
        """Generate PDF resume from formatted content.
        
        Args:
            content: Formatted resume content
            template_id: ID of template to use (default: from config)
            
        Returns:
            dict: {
                'pdf_path': str,  # Path to generated PDF
                'overflow': bool, # True if content overflows single page
                'message': str    # Warning message if overflow occurs
            }
        """
        logger.info(f"Starting PDF generation with template_id: {template_id}")
        if template_id is None:
            template_id = self.get_default_template_id()
            logger.info(f"Using default template: {template_id}")
        try:
            # Validate template
            self.validate_template(template_id)
            template_info = self.get_template_info(template_id)
            logger.info(f"Using template: {template_info.file_path} (ID: {template_id})")
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate LaTeX content
                template = self.env.get_template(template_info.file_path)
                logger.info(f"Template content: {template.render(**content)[:200]}...")  # Log first 200 chars
                latex_content = template.render(**content)

                # Debug: Write the generated LaTeX to a debug file
                debug_path = os.path.join(temp_dir, 'resume_debug.tex')
                with open(debug_path, 'w') as debug_file:
                    debug_file.write(latex_content)

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

                    # Run xelatex twice to resolve references (required for fontspec)
                    for i in range(2):
                        process = subprocess.run(
                            ['xelatex', '-interaction=nonstopmode', 'resume.tex'],
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
                            # logger.error(f"Full LaTeX output:\n{process.stdout}")
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
                    # Generate unique filename with user_id, timestamp and sanitized job title
                    timestamp = int(time.time())
                    safe_job_title = re.sub(r'[^\w\-_]', '_', content.get('job_title', 'generated'))
                    output_filename = f"{user_id.split(' ')[0]}_{safe_job_title}_{template_id}_resume_{timestamp}_.pdf"
                    output_path = output_dir / output_filename
                    with open(pdf_path, 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())

                    logger.info(f"Successfully generated PDF resume at: {output_path} using template: {template_id}")
                    
                    # Check for single page overflow if template requires it
                    template_info = self.get_template_info(template_id)
                    overflow = False
                    message = ""
                    
                    if template_info.single_page:
                        with open(pdf_path, 'rb') as f:
                            pdf = PdfReader(f)
                            if len(pdf.pages) > 1:
                                overflow = True
                                message = "Warning: Content exceeds single page limit for this template"
                                logger.warning(message)
                    
                    return {
                        'pdf_path': str(output_path),
                        'overflow': overflow,
                        'message': message
                    }

                finally:
                    os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise

class StagingTemplateProcessor(LatexProcessor):
    """
    A specialized processor for staging templates that inherits from LatexProcessor.
    This class works with StagingLatexTemplate objects instead of LatexTemplate objects.
    """
    
    def __init__(self, db: Session):
        # Initialize the parent class
        super().__init__(db)
        # Override the templates with staging templates
        self._load_staging_templates()
    
    def _load_staging_templates(self):
        """Load staging templates from the database."""
        try:
            self.templates = self.db.query(models.StagingLatexTemplate).filter(models.StagingLatexTemplate.is_active == True).all()
            logger.info(f"Loaded {len(self.templates)} staging templates from the database")
        except Exception as e:
            logger.error(f"Error loading staging templates from database: {str(e)}")
            self.templates = []
            raise ValueError("Failed to load staging templates from the database")
    
    def get_staging_template_info(self, template_id: str) -> models.StagingLatexTemplate:
        """Get staging template metadata by ID."""
        for template in self.templates:
            if str(template.id) == template_id:
                return template
        raise ValueError(f"Staging template not found: {template_id}")
    
    def generate_staging_pdf(self, template_id: str, test_data: dict) -> str:
        """Generate PDF from staging template using test data."""
        try:
            # Get the staging template
            staging_template = self.get_staging_template_info(template_id)
            
            # Clean and validate the test data
            cleaned_data = self.validate_and_clean(test_data)
            
            # Use the configured Jinja2 environment to parse the template string
            template = self.env.from_string(staging_template.latex_code)
            
            # Render the template with the cleaned test data
            latex_content = template.render(**cleaned_data)
            
            # Use the parent class's PDF generation logic
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write LaTeX file
                tex_path = os.path.join(temp_dir, 'staging_preview.tex')
                with open(tex_path, 'w') as f:
                    f.write(latex_content)

                # Compile LaTeX to PDF
                original_dir = os.getcwd()
                os.chdir(temp_dir)

                try:
                    # Run xelatex twice to resolve references
                    for i in range(2):
                        process = subprocess.run(
                            ['xelatex', '-interaction=nonstopmode', 'staging_preview.tex'],
                            capture_output=True,
                            text=True
                        )
                        
                        if process.returncode != 0:
                            error_output = process.stderr if process.stderr else process.stdout
                            logger.error(f"PDF compilation failed: {error_output}")
                            raise Exception(f"PDF compilation failed: {error_output}")

                    # Check if PDF was created
                    pdf_path = os.path.join(temp_dir, 'staging_preview.pdf')
                    if not os.path.exists(pdf_path):
                        raise Exception("PDF file was not created")

                    # Create output directory if it doesn't exist
                    output_dir = Path(__file__).parent.parent / "output"
                    output_dir.mkdir(exist_ok=True)

                    # Generate unique filename
                    timestamp = int(time.time())
                    output_filename = f"staging_{staging_template.name}_{timestamp}.pdf"
                    output_path = output_dir / output_filename

                    # Copy PDF to output directory
                    with open(pdf_path, 'rb') as src, open(output_path, 'wb') as dst:
                        dst.write(src.read())

                    logger.info(f"Successfully generated staging PDF at: {output_path}")
                    return str(output_path)

                finally:
                    os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error generating staging PDF: {str(e)}")
            raise
