from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import List

from backend.app.database import get_db
from backend.app.models.student import Student
from backend.app.models.opportunity import Application, ApplicationRequiredSkill
from backend.app.models.skill import SkillsMaster, StudentSkill, SkillTrend
from backend.app.routers.auth import get_current_student
from backend.app.services.cache_service import CacheService

router = APIRouter(prefix="/analytics", tags=["Analytics & System Trends"])

@router.get("/overview")
async def get_analytics_overview(
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    app_res = await db.execute(
        select(Application).where(Application.student_id == current_user.id)
    )
    apps = app_res.scalars().all()
    total = len(apps)

    funnel = {
        "saved": 0,
        "applied": 0,
        "oa_scheduled": 0,
        "interview": 0,
        "offers": 0,
        "rejected": 0
    }

    interview_triggers = 0
    offer_triggers = 0

    for a in apps:
        status_lower = a.status.lower()
        if status_lower == "saved":
            funnel["saved"] += 1
        elif status_lower == "applied":
            funnel["applied"] += 1
        elif status_lower in ["oa_scheduled", "oa"]:
            funnel["oa_scheduled"] += 1
        elif status_lower in ["interview", "interviews"]:
            funnel["interview"] += 1
            interview_triggers += 1
        elif status_lower in ["offer", "offers"]:
            funnel["offers"] += 1
            offer_triggers += 1
            interview_triggers += 1
        elif status_lower == "rejected":
            funnel["rejected"] += 1

    interview_rate = interview_triggers / total if total > 0 else 0.0
    offer_rate = offer_triggers / total if total > 0 else 0.0

    # Skill deficits (grouped missing skills)
    req_skills_query = (
        select(SkillsMaster.skill_name, func.count(SkillsMaster.id))
        .join(ApplicationRequiredSkill, ApplicationRequiredSkill.skill_id == SkillsMaster.id)
        .join(Application, Application.id == ApplicationRequiredSkill.application_id)
        .where(Application.student_id == current_user.id)
    )
    
    student_skills_subquery = (
        select(StudentSkill.skill_id)
        .where(StudentSkill.student_id == current_user.id)
    )
    
    req_skills_query = req_skills_query.where(
        ~ApplicationRequiredSkill.skill_id.in_(student_skills_subquery)
    ).group_by(SkillsMaster.skill_name).order_by(func.count(SkillsMaster.id).desc()).limit(5)

    deficits_res = await db.execute(req_skills_query)
    
    deficits = []
    for row in deficits_res.all():
        deficits.append({
            "skill_name": row[0],
            "missing_count": row[1]
        })

    if not deficits:
        deficits = [
            {"skill_name": "Spring Boot", "missing_count": 0},
            {"skill_name": "Microservices", "missing_count": 0}
        ]

    return {
        "total_applications": total,
        "funnel": funnel,
        "rates": {
            "interview_rate": round(interview_rate, 2),
            "offer_rate": round(offer_rate, 2)
        },
        "skill_deficits": deficits
    }

@router.get("/market-trends")
async def get_market_trends(
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    # Try fetching from cache first
    cached_data = CacheService.get("market_trends")
    if cached_data:
        print("--- [CACHE] RETRIEVED MARKET TRENDS FROM CACHE ---")
        return cached_data

    # Query trends database table
    trends_res = await db.execute(
        select(SkillTrend).order_by(SkillTrend.demand_count.desc()).limit(5)
    )
    trends = trends_res.scalars().all()

    response_data = {}
    if not trends:
        response_data = {
            "measured_date": str(date.today()),
            "hottest_skills": [
                {"skill_name": "Kafka", "demand_count": 142, "growth_weekly": 0.32},
                {"skill_name": "Redis", "demand_count": 118, "growth_weekly": 0.18},
                {"skill_name": "Spring Boot", "demand_count": 95, "growth_weekly": 0.12},
                {"skill_name": "Docker", "demand_count": 87, "growth_weekly": 0.08}
            ],
            "recommendations": "Based on 32% growth in Kafka listings, integrating message queues in backend applications is highly advised."
        }
    else:
        hottest = []
        for t in trends:
            hottest.append({
                "skill_name": t.skill_name,
                "demand_count": t.demand_count,
                "growth_weekly": t.trend_percentage / 100.0
            })
        response_data = {
            "measured_date": str(date.today()),
            "hottest_skills": hottest,
            "recommendations": "Focus on cloud-native backend skills (Docker, Spring Boot) showing positive trend growth."
        }

    # Store in cache for 300 seconds
    CacheService.set("market_trends", response_data, ttl=300)
    return response_data
