import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Date, DateTime, Float, func
from sqlalchemy.orm import relationship
from backend.app.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    raw_description = Column(Text, nullable=False)
    deadline = Column(Date, nullable=False)
    source_platform = Column(String(50), nullable=False)
    application_url = Column(String(255), nullable=True)
    status = Column(String(30), nullable=False, default="SAVED")
    priority_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="applications")
    required_skills = relationship("ApplicationRequiredSkill", back_populates="application", cascade="all, delete-orphan")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")


class ApplicationRequiredSkill(Base):
    __tablename__ = "application_required_skills"

    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(String, ForeignKey("skills_master.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    application = relationship("Application", back_populates="required_skills")
    skill = relationship("SkillsMaster", back_populates="application_associations")


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    application = relationship("Application", back_populates="status_history")
