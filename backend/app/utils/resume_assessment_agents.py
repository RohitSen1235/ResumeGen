from crewai import Agent, Task, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Content Quality Assessment Agent
content_quality_agent = Agent(
    role="Resume Content Quality Analyst",
    goal="Assess and improve the quality of resume content",
    backstory="""You are an expert in resume writing and content analysis.
    You have helped thousands of job seekers craft compelling resumes that
    effectively showcase their skills and experience.""",
    llm=LLM(model="gemini/gemini-1.5-flash",
            provider="google",
            verbose=True,
            temperature=0.5,  # Lower temperature for more focused analysis
            api_key=os.getenv("GOOGLE_API_KEY")),
    verbose=True
)

# # Formatting Analysis Agent
# formatting_agent = Agent(
#     role="Resume Formatting Specialist", 
#     goal="Analyze and optimize resume formatting and structure",
#     backstory="""You are a professional resume formatter with extensive 
#     experience in creating visually appealing and well-structured resumes 
#     that pass ATS systems and impress hiring managers.""",
#     llm=my_llm,
#     verbose=True
# )

# Skills Extraction and Matching Agent
skills_agent = Agent(
    role="Skills Matching Expert",
    goal="Extract and match skills from resume to job requirements",
    backstory="""You are a career coach specializing in helping candidates 
    align their skills with job descriptions. You have a deep understanding 
    of skill taxonomy and matching strategies.""",
    llm=LLM(model="gemini/gemini-1.5-flash",
            provider="google",
            verbose=True,
            temperature=0.5,  # Moderate temperature for skills analysis
            api_key=os.getenv("GOOGLE_API_KEY")),
    verbose=True
)

# Experience Validation Agent
experience_agent = Agent(
    role="Experience Validator",
    goal="Verify and optimize work experience descriptions",
    backstory="""You are a hiring manager with years of experience reviewing 
    resumes. You know exactly what makes work experience descriptions stand 
    out and get noticed by recruiters.""",
    llm=LLM(model="gemini/gemini-1.5-flash",
            provider="google",
            verbose=True,
            temperature=0.7,  # Higher temperature for creative experience descriptions
            api_key=os.getenv("GOOGLE_API_KEY")),
    verbose=True
)

# Resume Construction Agent
resume_constructor_agent = Agent(
    role="Resume Construction Specialist",
    goal="Construct a well-structured resume from optimized content",
    backstory="""You are an expert in resume construction who takes optimized 
    content from various specialists and assembles it into a cohesive, 
    professional resume that is ready for PDF generation.""",
    llm=LLM(model="gemini/gemini-1.5-flash",
            provider="google",
            verbose=True,
            temperature=0.1,  # Very low temperature for precise resume construction
            api_key=os.getenv("GOOGLE_API_KEY")),
    verbose=True
)

# Create tasks for each agent with improved descriptions
content_quality_task = Task(
    description="""Analyze the following initial resume content for clarity, impact, and
    effectiveness. Provide specific suggestions for improvement.
    
    Initial Content and Job description:
    {task.context}

    
    Focus on:
    - Using concise, easy-to-understand language
    - Incorporating strong action verbs (e.g., 'led', 'developed', 'optimized')
    - Quantifying achievements (e.g., 'Increased sales by 25%')
    - Creating a compelling narrative
    
    Example of improved content:
    Before: 'Managed a team of developers'
    After: 'Led a team of 5 developers to deliver 3 major projects 2 weeks ahead of schedule'
    
    Provide a quality score (1-10) based on:
    - Clarity (30%)
    - Impact (30%)
    - Effectiveness (40%)""",
    agent=content_quality_agent,
    expected_output="A detailed analysis of the resume content quality with specific improvement suggestions and a quality score"
)

# formatting_task = Task(
#     description="""Review the following initial resume content's formatting and structure. Ensure it is
#         ATS-friendly and visually appealing. Provide formatting recommendations.
        
#     Initial Content and Job description:
#     {task.context}
        
#     Check for:
#     - Standard fonts (Arial, Calibri, Times New Roman)
#     - Consistent spacing and margins
#     - Clear section headings
#     - Proper use of bullet points
#     - Avoidance of tables, graphics, and columns
    
#     Example of improved formatting:
#     Before: 'Skills: Python, Java, SQL'
#     After: '• Python\n• Java\n• SQL'
    
#     Provide a formatting score (1-10) based on:
#     - ATS compatibility (40%)
#     - Visual appeal (30%)
#     - Readability (30%)""",
#     agent=formatting_agent,
#     expected_output="A detailed analysis of resume formatting with specific recommendations for improvement and a formatting score"
# )

skills_task = Task(
    description="""Extract skills from the following initial resume content and match them to the
        provided job description. Identify any gaps and suggest improvements.
        
    Initial Content and Job description:
    {task.context}
        
    Analyze:
    - Hard skills (e.g., programming languages, tools)
    - Soft skills (e.g., communication, leadership)
    - Transferable skills
    
    Example of improved skills section:
    Before: 'Experienced in Python'
    After: '• Python: Developed 3 web applications using Django framework'
    
    Provide a skills match score (1-10) based on:
    - Relevance to job description (50%)
    - Depth of skill description (30%)
    - Transferability (20%)""",
    agent=skills_agent,
    expected_output="A detailed skills analysis showing matched skills, gaps, improvement suggestions, and a skills match score"
)

experience_task = Task(
    description="""Validate the work experience descriptions in the following initial resume content. Ensure they
        are achievement-oriented and quantify results where possible.
        
    Initial Content and Job description:
    {task.context}
        
    Apply the STAR method:
    - Situation: Context of the task
    - Task: Specific responsibilities
    - Action: Steps taken
    - Result: Quantifiable outcomes
    
    Example of improved experience:
    Before: 'Managed social media accounts'
    After: 'Increased social media engagement by 40% through targeted content strategy and analytics-driven optimization'
    
    Provide an experience quality score (1-10) based on:
    - Achievement orientation (40%)
    - Quantification of results (30%)
    - STAR method application (30%)""",
    agent=experience_agent,
    expected_output="A detailed analysis of work experience descriptions with specific recommendations for improvement and an experience quality score"
)

resume_construction_task = Task(
    description="""Construct a final resume from the optimized content provided by the other agents.
    Ensure the resume is properly structured and formatted for PDF generation.
    
    Input Content:
    {task.context}
    
    Requirements:
    - Organize content into standard resume sections
    - Maintain consistent formatting
    - Ensure all content is properly structured for LaTeX processing
    - Remove any redundant or conflicting information
    - Verify all section headers and markers are present
    
    Output Format:
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
            """,
    agent=resume_constructor_agent,
    expected_output="A well-structured resume ready for PDF generation"
)