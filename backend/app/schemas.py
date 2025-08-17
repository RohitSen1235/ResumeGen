from pydantic import BaseModel, EmailStr, Field
from pydantic.types import UUID4, conlist
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime, date

class Position(BaseModel):
    id: str
    title: str
    company_name: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None
    is_current: Optional[bool] = False

class Education(BaseModel):
    id: str
    school_name: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    description: Optional[str] = None

class Skill(BaseModel):
    id: str
    name: str
    proficiency: Optional[str] = None

class LinkedInProfile(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    summary: Optional[str] = None
    positions: conlist(Position, max_length=50) = Field(default_factory=list)
    education: conlist(Education, max_length=20) = Field(default_factory=list)
    skills: conlist(Skill, max_length=100) = Field(default_factory=list)

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    user_type: Optional[Literal["student", "job_seeker", "career_changer", "other"]] = None

class UserCreateAdmin(UserCreate):
    is_admin: bool = False

class UserUpdateAdmin(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    user_type: Optional[Literal["student", "job_seeker", "career_changer", "other"]] = None

class UserCreateOAuth(UserBase):
    oauth_provider: str
    oauth_id: str

class UserLogin(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ProfileBase(BaseModel):
    name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    github_url: Optional[str] = None
    professional_title: Optional[str] = None
    summary: Optional[str] = None
    resume_path: Optional[str] = None
    use_resume_as_reference: Optional[bool] = True
    use_resume_sections: Optional[bool] = True
    professional_info: Optional[Dict[str, Any]] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    onboarding_completed: Optional[bool] = None

class Profile(ProfileBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class User(UserBase):
    id: UUID4
    is_admin: bool = False
    user_type: Optional[Literal["student", "job_seeker", "career_changer", "other"]] = None
    credits: int = 0
    onboarding_completed: bool = False
    created_at: datetime
    updated_at: Optional[datetime]
    profile: Optional[Profile] = None

    class Config:
        from_attributes = True


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserCreditUpdate(BaseModel):
    user_id: UUID4
    credits: int
    operation: Literal["add", "set"]

# Profile Section Schemas

class WorkExperienceBase(BaseModel):
    position: str
    company: str
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current_job: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = None
    technologies: Optional[List[str]] = None

class WorkExperienceCreate(WorkExperienceBase):
    pass

class WorkExperienceUpdate(WorkExperienceBase):
    position: Optional[str] = None
    company: Optional[str] = None

class WorkExperience(WorkExperienceBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class EducationBase(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    description: Optional[str] = None
    achievements: Optional[List[str]] = None

class EducationCreate(EducationBase):
    pass

class EducationUpdate(EducationBase):
    institution: Optional[str] = None
    degree: Optional[str] = None

class EducationSection(EducationBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    proficiency: Optional[Literal["Beginner", "Intermediate", "Advanced", "Expert"]] = None
    years_experience: Optional[int] = None

class SkillCreate(SkillBase):
    pass

class SkillUpdate(SkillBase):
    name: Optional[str] = None

class SkillSection(SkillBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    technologies: Optional[List[str]] = None
    achievements: Optional[List[str]] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None

class Project(ProjectBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class PublicationBase(BaseModel):
    title: str
    publisher: Optional[str] = None
    publication_date: Optional[date] = None
    url: Optional[str] = None
    description: Optional[str] = None
    authors: Optional[List[str]] = None

class PublicationCreate(PublicationBase):
    pass

class PublicationUpdate(PublicationBase):
    title: Optional[str] = None

class Publication(PublicationBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class VolunteerWorkBase(BaseModel):
    organization: str
    role: str
    cause: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current_role: Optional[bool] = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = None

class VolunteerWorkCreate(VolunteerWorkBase):
    pass

class VolunteerWorkUpdate(VolunteerWorkBase):
    organization: Optional[str] = None
    role: Optional[str] = None

class VolunteerWork(VolunteerWorkBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Resume parsing schema for Groq AI
class ResumeParseRequest(BaseModel):
    resume_text: str

class ResumeParseResponse(BaseModel):
    work_experience: List[WorkExperienceBase] = Field(default_factory=list)
    education: List[EducationBase] = Field(default_factory=list)
    skills: List[SkillBase] = Field(default_factory=list)
    projects: List[ProjectBase] = Field(default_factory=list)
    publications: List[PublicationBase] = Field(default_factory=list)
    volunteer_work: List[VolunteerWorkBase] = Field(default_factory=list)
    summary: Optional[str] = None
    professional_title: Optional[str] = None

class ResumeContentUpdate(BaseModel):
    content: str
