from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Index, Boolean, Integer, Text, Date, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)  # Make nullable for OAuth users
    oauth_provider = Column(String, nullable=True)  # 'linkedin', 'google', etc.
    oauth_id = Column(String, nullable=True)  # Provider's user ID
    is_admin = Column(Boolean, default=False, nullable=False)
    user_type = Column(String, nullable=True)  # student, job_seeker, career_changer, other
    credits = Column(Integer, default=0, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with Profile
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String)
    phone = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    portfolio_url = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    professional_title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    resume_path = Column(String, nullable=True)
    use_resume_as_reference = Column(Boolean, default=True, nullable=False)  # Whether to use uploaded resume as reference
    use_resume_sections = Column(Boolean, default=True, nullable=False)  # Whether to use profile sections for resume generation
    professional_info = Column(JSON, nullable=True)  # Legacy field - kept for backward compatibility
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with User
    user = relationship("User", back_populates="profile")
    
    # Relationship with Resumes
    resumes = relationship("Resume", back_populates="profile")
    
    # Relationships with profile sections
    work_experiences = relationship("WorkExperience", back_populates="profile", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="profile", cascade="all, delete-orphan")
    volunteer_works = relationship("VolunteerWork", back_populates="profile", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    content = Column(String)  # Stores the complete resume text
    job_description = Column(String)  # The job description this resume was optimized for
    name = Column(String)  # User-defined name for the resume
    version = Column(String)  # Resume version/type
    status = Column(String, default='pending')  # Generation status: pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="resumes")

    __table_args__ = (
        Index('ix_resumes_profile_id_status', 'profile_id', 'status'),
        Index('ix_resumes_created_at', 'created_at'),
    )

class WorkExperience(Base):
    __tablename__ = "work_experiences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    position = Column(String, nullable=False)
    company = Column(String, nullable=False)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    current_job = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    achievements = Column(JSON, nullable=True)  # Array of achievement strings
    technologies = Column(JSON, nullable=True)  # Array of technology strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="work_experiences")

class Education(Base):
    __tablename__ = "educations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    field_of_study = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    gpa = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    achievements = Column(JSON, nullable=True)  # Array of achievement strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="educations")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)  # e.g., "Programming", "Languages", "Tools"
    proficiency = Column(String, nullable=True)  # e.g., "Beginner", "Intermediate", "Advanced", "Expert"
    years_experience = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="skills")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    technologies = Column(JSON, nullable=True)  # Array of technology strings
    achievements = Column(JSON, nullable=True)  # Array of achievement strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="projects")

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=True)
    publication_date = Column(Date, nullable=True)
    url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    authors = Column(JSON, nullable=True)  # Array of author names
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="publications")

class VolunteerWork(Base):
    __tablename__ = "volunteer_works"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), index=True)
    organization = Column(String, nullable=False)
    role = Column(String, nullable=False)
    cause = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    current_role = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    achievements = Column(JSON, nullable=True)  # Array of achievement strings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="volunteer_works")
