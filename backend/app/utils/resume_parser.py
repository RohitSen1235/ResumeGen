import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
import json
import re

logger = logging.getLogger(__name__)

class ResumeParser:
    @staticmethod
    def parse_linkedin_profile(profile_url: str) -> dict:
        """
        Scrape professional information from LinkedIn profile.
        """
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Initialize the Chrome WebDriver
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )

            try:
                # Load the LinkedIn profile
                driver.get(profile_url)
                
                # Wait for the content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "core-section"))
                )

                # Get the page source
                soup = BeautifulSoup(driver.page_source, 'html.parser')

                # Extract professional information
                experience = []
                experience_sections = soup.find_all('section', {'class': 'experience-section'})
                for section in experience_sections:
                    positions = section.find_all('div', {'class': 'experience-item'})
                    for position in positions:
                        title = position.find('h3', {'class': 'title'}).text.strip()
                        company = position.find('p', {'class': 'company'}).text.strip()
                        duration = position.find('span', {'class': 'date-range'}).text.strip()
                        description = position.find('p', {'class': 'description'})
                        description_text = description.text.strip() if description else ""
                        
                        experience.append({
                            "title": title,
                            "company": company,
                            "duration": duration,
                            "achievements": [description_text] if description_text else []
                        })

                # Extract education
                education = []
                education_sections = soup.find_all('section', {'class': 'education-section'})
                for section in education_sections:
                    schools = section.find_all('div', {'class': 'education-item'})
                    for school in schools:
                        degree = school.find('h3', {'class': 'degree'}).text.strip()
                        institution = school.find('p', {'class': 'school'}).text.strip()
                        year = school.find('span', {'class': 'date-range'}).text.strip()
                        
                        education.append({
                            "degree": degree,
                            "institution": institution,
                            "year": year,
                            "details": []
                        })

                # Extract skills
                skills = []
                skills_section = soup.find('section', {'class': 'skills-section'})
                if skills_section:
                    skill_items = skills_section.find_all('span', {'class': 'skill'})
                    skills = [skill.text.strip() for skill in skill_items]

                return {
                    "experience": experience,
                    "education": education,
                    "skills": skills
                }

            finally:
                driver.quit()

        except Exception as e:
            logger.error(f"Error parsing LinkedIn profile: {str(e)}")
            raise

    @staticmethod
    def parse_pdf_resume(file_path: str) -> dict:
        """
        Extract professional information from PDF resume.
        """
        try:
            # Extract text from PDF
            text = extract_text(file_path)
            
            # Split into sections
            sections = text.split('\n\n')
            
            # Initialize data structure
            data = {
                "experience": [],
                "education": [],
                "skills": []
            }
            
            current_section = None
            
            # Process each section
            for section in sections:
                section = section.strip()
                
                # Skip empty sections
                if not section:
                    continue
                
                # Identify sections
                if re.search(r'experience|work|employment', section.lower()):
                    current_section = "experience"
                    continue
                elif re.search(r'education|academic|qualification', section.lower()):
                    current_section = "education"
                    continue
                elif re.search(r'skills|expertise|competencies', section.lower()):
                    current_section = "skills"
                    continue
                
                # Process sections
                if current_section == "experience":
                    # Try to extract job details
                    if re.search(r'\d{4}', section):  # Look for years to identify job entries
                        title_match = re.search(r'^(.+?(?=\sat\s|\s-\s|$))', section)
                        company_match = re.search(r'at\s(.+?(?=\s\d{4}|\s-\s|$))', section)
                        duration_match = re.search(r'\d{4}\s*-\s*(?:\d{4}|present)', section, re.IGNORECASE)
                        
                        if title_match:
                            experience_entry = {
                                "title": title_match.group(1).strip(),
                                "company": company_match.group(1).strip() if company_match else "",
                                "duration": duration_match.group(0) if duration_match else "",
                                "achievements": [line.strip() for line in section.split('\n') if line.strip() and not line.strip().startswith(('•', '-'))]
                            }
                            data["experience"].append(experience_entry)
                
                elif current_section == "education":
                    # Try to extract education details
                    if re.search(r'\d{4}', section):  # Look for years to identify education entries
                        degree_match = re.search(r'^(.+?(?=\sat\s|\s-\s|$))', section)
                        institution_match = re.search(r'at\s(.+?(?=\s\d{4}|\s-\s|$))', section)
                        year_match = re.search(r'\d{4}', section)
                        
                        if degree_match:
                            education_entry = {
                                "degree": degree_match.group(1).strip(),
                                "institution": institution_match.group(1).strip() if institution_match else "",
                                "year": year_match.group(0) if year_match else "",
                                "details": []
                            }
                            data["education"].append(education_entry)
                
                elif current_section == "skills":
                    # Extract skills
                    skills = [skill.strip() for skill in re.split(r'[,•]', section) if skill.strip()]
                    data["skills"].extend(skills)
            
            return data

        except Exception as e:
            logger.error(f"Error parsing PDF resume: {str(e)}")
            raise

    @staticmethod
    def get_professional_info(linkedin_url: str = None, resume_file: str = None) -> dict:
        """
        Get professional information from either LinkedIn profile or PDF resume.
        """
        if linkedin_url:
            return ResumeParser.parse_linkedin_profile(linkedin_url)
        elif resume_file:
            return ResumeParser.parse_pdf_resume(resume_file)
        else:
            raise ValueError("Either LinkedIn profile URL or resume file path must be provided")
