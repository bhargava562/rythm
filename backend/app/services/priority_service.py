import os
from datetime import date
from typing import List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.student import StudentProfile
from backend.app.models.opportunity import Application
from backend.app.models.skill import StudentSkill, ApplicationRequiredSkill, SkillTrend

WEIGHT_URGENCY = float(os.getenv("WEIGHT_URGENCY", 0.30))
WEIGHT_SKILL_MATCH = float(os.getenv("WEIGHT_SKILL_MATCH", 0.40))
WEIGHT_TREND_RELEVANCE = float(os.getenv("WEIGHT_TREND_RELEVANCE", 0.15))
WEIGHT_STUDENT_INTEREST = float(os.getenv("WEIGHT_STUDENT_INTEREST", 0.15))

class PriorityService:
    @staticmethod
    def calculate_urgency(deadline: date) -> float:
        """Urgency score from 0.1 to 1.0 (linear decay over 30 days)."""
        today = date.today()
        delta = (deadline - today).days
        if delta <= 0:
            return 1.0
        if delta >= 30:
            return 0.1
        return max(0.1, min(1.0, 1.0 - (delta / 30.0)))

    @staticmethod
    def calculate_interest(role: str, target_roles: List[str]) -> float:
        """Interest fit based on role string similarity checks."""
        if not target_roles:
            return 0.5
            
        role_lower = role.lower()
        for target in target_roles:
            target_lower = target.lower()
            if target_lower == role_lower:
                return 1.0
            if target_lower in role_lower or role_lower in target_lower:
                return 0.7
        return 0.2

    @classmethod
    async def recalculate_priority(cls, db: AsyncSession, application_id: str) -> float:
        app_result = await db.execute(
            select(Application).where(Application.id == application_id)
        )
        application = app_result.scalar_one_or_none()
        if not application:
            return 0.0

        student_id = application.student_id

        # Profile targets
        profile_result = await db.execute(
            select(StudentProfile).where(StudentProfile.student_id == student_id)
        )
        profile = profile_result.scalar_one_or_none()
        target_roles = profile.target_roles if profile else []

        # Calculation factors
        urgency_score = cls.calculate_urgency(application.deadline)

        # Skills match calculation
        req_skills_result = await db.execute(
            select(ApplicationRequiredSkill.skill_id).where(ApplicationRequiredSkill.application_id == application_id)
        )
        required_skill_ids = [r[0] for r in req_skills_result.all()]

        stud_skills_result = await db.execute(
            select(StudentSkill.skill_id).where(StudentSkill.student_id == student_id)
        )
        student_skill_ids = [s[0] for s in stud_skills_result.all()]

        if not required_skill_ids:
            skill_match_score = 1.0
        else:
            intersection = set(required_skill_ids).intersection(set(student_skill_ids))
            skill_match_score = len(intersection) / len(required_skill_ids)

        # Trend check
        trend_score = 0.2
        if required_skill_ids:
            trending_result = await db.execute(
                select(SkillTrend.skill_name).where(SkillTrend.trend_percentage > 10.0)
            )
            trending_skills = [t[0].lower() for t in trending_result.all()]
            trend_score = 0.5 # Default fallback score

        interest_score = cls.calculate_interest(application.role, target_roles)

        # Calculate final priority score
        priority = (
            (WEIGHT_URGENCY * urgency_score) +
            (WEIGHT_SKILL_MATCH * skill_match_score) +
            (WEIGHT_TREND_RELEVANCE * trend_score) +
            (WEIGHT_STUDENT_INTEREST * interest_score)
        )
        priority = max(0.0, min(1.0, priority))
        
        application.priority_score = priority
        db.add(application)
        await db.flush()

        return priority
