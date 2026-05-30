from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.student import Student
from backend.app.models.opportunity import Application, ApplicationRequiredSkill, ApplicationStatusHistory
from backend.app.models.skill import SkillsMaster, StudentSkill
from backend.app.schemas.opportunity import (
    ApplicationIngest,
    ApplicationIngestOut,
    ApplicationOut,
    ApplicationStatusTransition,
    ResumeTailorRequest,
    ResumeTailorResponse
)
from backend.app.services.ai_service import AIService
from backend.app.services.priority_service import PriorityService
from backend.app.services.resume_service import ResumeService
from backend.app.services.cache_service import CacheService
from backend.app.routers.auth import get_current_student

router = APIRouter(prefix="/applications", tags=["Opportunities Tracking"])

@router.post("/ingest", response_model=ApplicationIngestOut, status_code=status.HTTP_201_CREATED)
async def ingest_opportunity(
    app_in: ApplicationIngest,
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    # Ingestion setup
    new_app = Application(
        student_id=current_user.id,
        company_name=app_in.company_name,
        role=app_in.role,
        raw_description=app_in.job_description_text,
        deadline=app_in.deadline,
        source_platform=app_in.source_platform,
        application_url=app_in.application_url,
        status="SAVED"
    )
    db.add(new_app)
    await db.flush()

    # Extract requirements
    ai_result = await AIService.extract_skills_from_jd(app_in.job_description_text)
    extracted_skills = ai_result.get("skills", [])
    extracted_domain = ai_result.get("domain", "Software Engineering")
    extracted_exp_level = ai_result.get("experience_level", "Intern")

    required_skill_names = []
    for skill_name in extracted_skills:
        cat_res = await db.execute(select(SkillsMaster).where(SkillsMaster.skill_name == skill_name))
        master_skill = cat_res.scalar_one_or_none()
        if not master_skill:
            master_skill = SkillsMaster(skill_name=skill_name, category="General")
            db.add(master_skill)
            await db.flush()
        
        req_link = ApplicationRequiredSkill(application_id=new_app.id, skill_id=master_skill.id)
        db.add(req_link)
        required_skill_names.append(master_skill.skill_name)

    await db.flush()

    # Get student skills for gap analysis
    stud_skills_res = await db.execute(
        select(SkillsMaster.skill_name)
        .join(StudentSkill, StudentSkill.skill_id == SkillsMaster.id)
        .where(StudentSkill.student_id == current_user.id)
    )
    student_skills = [row[0] for row in stud_skills_res.all()]

    matching = list(set(required_skill_names).intersection(set(student_skills)))
    missing = list(set(required_skill_names) - set(student_skills))
    match_score = len(matching) / len(required_skill_names) if required_skill_names else 1.0

    # Calculate dynamic priority score
    priority_score = await PriorityService.recalculate_priority(db, new_app.id)
    await db.commit()
    await db.refresh(new_app)

    # Invalidate cached trends
    CacheService.delete("market_trends")

    return {
        "id": new_app.id,
        "company_name": new_app.company_name,
        "role": new_app.role,
        "status": new_app.status,
        "priority_score": priority_score,
        "ai_analysis": {
            "extracted_domain": extracted_domain,
            "extracted_experience_level": extracted_exp_level,
            "required_skills": required_skill_names,
            "match_score": match_score,
            "matching_skills": matching,
            "missing_skills": missing
        }
    }

@router.get("", response_model=List[ApplicationOut])
async def list_opportunities(
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    query = select(Application).where(Application.student_id == current_user.id)
    if status:
        query = query.where(Application.status == status)
    if search:
        query = query.where(
            (Application.company_name.ilike(f"%{search}%")) |
            (Application.role.ilike(f"%{search}%"))
        )
    query = query.order_by(Application.priority_score.desc())
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.patch("/{id}/status")
async def transition_status(
    id: str,
    transition: ApplicationStatusTransition,
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Application).where(
            (Application.id == id) & (Application.student_id == current_user.id)
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    old_status = application.status
    new_status = transition.new_status

    application.status = new_status
    db.add(application)

    history = ApplicationStatusHistory(
        application_id=application.id,
        old_status=old_status,
        new_status=new_status,
        notes=transition.notes
    )
    db.add(history)
    
    await PriorityService.recalculate_priority(db, application.id)
    await db.commit()

    return {
        "application_id": application.id,
        "old_status": old_status,
        "new_status": new_status,
        "transitioned_at": history.changed_at
    }

@router.post("/{id}/resume-tailor", response_model=ResumeTailorResponse)
async def tailor_resume(
    id: str,
    resume_req: ResumeTailorRequest,
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Application).where(
            (Application.id == id) & (Application.student_id == current_user.id)
        )
    )
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Required skills list
    req_skills_res = await db.execute(
        select(SkillsMaster.skill_name)
        .join(ApplicationRequiredSkill, ApplicationRequiredSkill.skill_id == SkillsMaster.id)
        .where(ApplicationRequiredSkill.application_id == id)
    )
    required_skills = [row[0] for row in req_skills_res.all()]

    # Student skills list
    stud_skills_res = await db.execute(
        select(SkillsMaster.skill_name)
        .join(StudentSkill, StudentSkill.skill_id == SkillsMaster.id)
        .where(StudentSkill.student_id == current_user.id)
    )
    student_skills = [row[0] for row in stud_skills_res.all()]

    matching = list(set(required_skills).intersection(set(student_skills)))
    missing = list(set(required_skills) - set(student_skills))
    matching_score_estimate = len(matching) / len(required_skills) if required_skills else 1.0

    suggestions = await ResumeService.generate_resume_suggestions(
        company_name=application.company_name,
        role=application.role,
        resume_text=resume_req.raw_resume_text,
        required_skills=required_skills,
        missing_skills=missing,
        student_skills=student_skills
    )

    return {
        "application_id": application.id,
        "target_role": f"{application.role} ({application.company_name})",
        "matching_score_estimate": matching_score_estimate,
        "suggestions": suggestions
    }
