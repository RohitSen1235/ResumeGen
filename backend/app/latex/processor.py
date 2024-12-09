import os
import subprocess
import tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PyPDF2 import PdfWriter, PdfReader
import logging
import shutil

logger = logging.getLogger(__name__)

class LatexProcessor:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.assets_dir = Path(__file__).parent / "assets"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            # Use different delimiters to avoid conflict with LaTeX
            block_start_string='[%',
            block_end_string='%]',
            variable_start_string='[[',
            variable_end_string=']]',
            comment_start_string='[#',
            comment_end_string='#]',
            trim_blocks=True,
            autoescape=False,
        )

    def create_watermark(self, output_path: str, text: str = "Generated by Resume Builder"):
        """Create a watermark PDF with diagonal text."""
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Set up the watermark properties
        c.setFillColorRGB(0.8, 0.8, 0.8, 0.3)  # Light gray, 30% opacity
        c.setFont("Helvetica", 24)
        
        # Rotate and position the text
        c.saveState()
        c.translate(width/2, height/2)
        c.rotate(45)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        
        c.save()

    def add_watermark(self, input_pdf: str, watermark_pdf: str, output_pdf: str):
        """Add watermark to the PDF."""
        try:
            with open(input_pdf, 'rb') as file:
                pdf_reader = PdfReader(file)
                pdf_writer = PdfWriter()

                with open(watermark_pdf, 'rb') as watermark_file:
                    watermark = PdfReader(watermark_file)
                    watermark_page = watermark.pages[0]

                    for page in pdf_reader.pages:
                        page.merge_page(watermark_page)
                        pdf_writer.add_page(page)

                with open(output_pdf, 'wb') as output_file:
                    pdf_writer.write(output_file)

        except Exception as e:
            logger.error(f"Error adding watermark: {str(e)}")
            raise

    def verify_latex_installation(self):
        """Verify that LaTeX is installed and accessible."""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, 
                                  text=True)
            if result.returncode != 0:
                logger.error("LaTeX is not properly installed")
                logger.error(f"Error output: {result.stderr}")
                return False
            return True
        except FileNotFoundError:
            logger.error("pdflatex command not found. Please install LaTeX.")
            return False

    def compile_latex(self, tex_path: str, output_dir: str) -> str:
        """Compile LaTeX file to PDF."""
        if not self.verify_latex_installation():
            raise Exception("LaTeX is not properly installed")

        try:
            # Change to output directory for compilation
            original_dir = os.getcwd()
            os.chdir(output_dir)

            try:
                tex_filename = os.path.basename(tex_path)
                # Run pdflatex twice to ensure proper rendering
                for i in range(2):
                    logger.info(f"LaTeX compilation attempt {i+1}")
                    process = subprocess.Popen(
                        ['pdflatex', '-interaction=nonstopmode', tex_filename],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout, stderr = process.communicate()

                    # Log the output
                    logger.info(f"LaTeX stdout: {stdout.decode()}")
                    if stderr:
                        logger.error(f"LaTeX stderr: {stderr.decode()}")

                    if process.returncode != 0:
                        # Read the log file if it exists
                        log_file = os.path.join(output_dir, tex_filename.replace('.tex', '.log'))
                        if os.path.exists(log_file):
                            with open(log_file, 'r') as f:
                                log_content = f.read()
                                logger.error(f"LaTeX log file contents: {log_content}")
                        
                        raise Exception(f"LaTeX compilation failed with return code {process.returncode}")

                # Check if PDF was actually created
                pdf_path = os.path.join(output_dir, tex_filename.replace('.tex', '.pdf'))
                if not os.path.exists(pdf_path):
                    raise Exception("PDF file was not created")

                return pdf_path

            finally:
                # Always return to original directory
                os.chdir(original_dir)

        except Exception as e:
            logger.error(f"Error compiling LaTeX: {str(e)}")
            raise

    def generate_resume_pdf(self, content: dict) -> str:
        """Generate a PDF resume from the provided content."""
        try:
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Render LaTeX template
                template = self.env.get_template('resume.tex.j2')
                latex_content = template.render(**content)

                # Log the generated LaTeX content for debugging
                logger.info(f"Generated LaTeX content:\n{latex_content}")

                # Save LaTeX content to temporary file
                tex_path = os.path.join(temp_dir, 'resume.tex')
                with open(tex_path, 'w') as f:
                    f.write(latex_content)

                # Compile LaTeX to PDF
                pdf_path = self.compile_latex(tex_path, temp_dir)

                # Create watermark
                watermark_path = os.path.join(temp_dir, 'watermark.pdf')
                self.create_watermark(watermark_path)

                # Add watermark to PDF
                final_pdf_path = os.path.join(temp_dir, 'resume_final.pdf')
                self.add_watermark(pdf_path, watermark_path, final_pdf_path)

                # Copy the final PDF to a permanent location
                output_dir = Path(__file__).parent.parent / "output"
                output_dir.mkdir(exist_ok=True)
                
                final_output_path = output_dir / f"resume_{content.get('job_title', 'generated')}.pdf"
                with open(final_pdf_path, 'rb') as src, open(final_output_path, 'wb') as dst:
                    dst.write(src.read())

                return str(final_output_path)

        except Exception as e:
            logger.error(f"Error generating resume PDF: {str(e)}")
            raise

    def format_content(self, personal_info: dict, ai_content: str, job_title: str, professional_info: dict = None) -> dict:
        """Format AI-generated content and personal information into template-compatible structure."""
        try:
            # Validate required personal information
            if not personal_info.get('name'):
                raise ValueError("Name is required in personal information")
            if not personal_info.get('email'):
                raise ValueError("Email is required in personal information")

            # Initialize formatted content with personal information
            formatted_content = {
                "name": personal_info['name'],
                "email": personal_info['email'],
                "phone": personal_info.get('phone', ''),  # Optional
                "location": personal_info.get('location', ''),  # Optional
                "linkedin": personal_info.get('linkedin', ''),  # Optional
                "job_title": job_title,
                "summary": "",
                "skills": [],
                "experience": [],
                "education": [],
                "certifications": []
            }

            # Use professional information if available
            if professional_info:
                formatted_content.update({
                    "skills": professional_info.get('skills', []),
                    "experience": professional_info.get('experience', []),
                    "education": professional_info.get('education', [])
                })

            # Parse AI-generated content sections
            sections = ai_content.split('\n\n')
            for section in sections:
                if "Professional Summary" in section:
                    formatted_content["summary"] = section.split("Professional Summary")[-1].strip()
                elif "Key Skills" in section and not formatted_content["skills"]:
                    # Only use AI-generated skills if no professional info is available
                    skills_text = section.split("Key Skills")[-1].strip()
                    formatted_content["skills"] = [
                        skill.strip() for skill in skills_text.split('\n')
                        if skill.strip() and not skill.strip().startswith(('-', '•'))
                    ]

            logger.info(f"Formatted content: {formatted_content}")
            return formatted_content

        except Exception as e:
            logger.error(f"Error formatting content: {str(e)}")
            raise
