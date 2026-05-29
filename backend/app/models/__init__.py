from backend.app.database import Base
from backend.app.models.student import Student, StudentProfile
from backend.app.models.skill import SkillsMaster, StudentSkill, SkillTrend
from backend.app.models.opportunity import Application, ApplicationRequiredSkill, ApplicationStatusHistory

__all__ = [
    "Base",
    "Student",
    "StudentProfile",
    "SkillsMaster",
    "StudentSkill",
    "SkillTrend",
    "Application",
    "ApplicationRequiredSkill",
    "ApplicationStatusHistory",
]
