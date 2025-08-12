from pydantic import BaseModel, EmailStr, Field
from pydantic.types import UUID4, conlist
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime

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
    resume_path: Optional[str] = None
    use_resume_as_reference: Optional[bool] = True
    professional_info: Optional[Dict[str, Any]] = None

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

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
