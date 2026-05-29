import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, ARRAY, func
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    college_name = Column(String(150), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    branch = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False, default="student") # student, admin, etc.
    reset_token = Column(String(255), nullable=True) # for simulated password reset
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("StudentProfile", back_populates="student", uselist=False, cascade="all, delete-orphan")
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="student", cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    bio = Column(String, nullable=True)
    target_roles = Column(ARRAY(String), nullable=False, default=[])
    github_url = Column(String(255), nullable=True)
    leetcode_url = Column(String(255), nullable=True)
    resume_url = Column(String(255), nullable=True)
    profile_strength = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="profile")
