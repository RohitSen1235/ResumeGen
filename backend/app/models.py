from sqlalchemy import Column, String, ForeignKey, JSON, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
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
    location = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    resume_path = Column(String, nullable=True)
    professional_info = Column(JSON, nullable=True)  # Stores parsed LinkedIn/resume data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with User
    user = relationship("User", back_populates="profile")
    
    # Relationship with Resumes
    resumes = relationship("Resume", back_populates="profile")

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
