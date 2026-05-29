import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Float, Date, func
from sqlalchemy.orm import relationship
from backend.app.database import Base

class SkillsMaster(Base):
    __tablename__ = "skills_master"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)

    # Relationships
    student_associations = relationship("StudentSkill", back_populates="skill")
    application_associations = relationship("ApplicationRequiredSkill", back_populates="skill")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    student_id = Column(String, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(String, ForeignKey("skills_master.id", ondelete="CASCADE"), primary_key=True)
    proficiency_level = Column(String(20), nullable=False, default="BEGINNER")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="skills")
    skill = relationship("SkillsMaster", back_populates="student_associations")


class SkillTrend(Base):
    __tablename__ = "skill_trends"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    skill_name = Column(String(100), unique=True, nullable=False, index=True)
    demand_count = Column(Integer, nullable=False, default=0)
    trend_percentage = Column(Float, nullable=False, default=0.0)
    measured_date = Column(Date, server_default=func.current_date())
