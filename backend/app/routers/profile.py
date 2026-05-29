from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.app.database import get_db
from backend.app.models.student import Student, StudentProfile
from backend.app.models.skill import SkillsMaster, StudentSkill
from backend.app.schemas.student import ProfileInitialize, ProfileOut
from backend.app.schemas.skill import StudentSkillsUpdate, StudentSkillOut
from backend.app.routers.auth import get_current_student

router = APIRouter(prefix="/profile", tags=["Student Profiles"])

def calculate_strength(profile: StudentProfile, skill_count: int) -> int:
    strength = 10
    if profile.bio:
        strength += 15
    if profile.target_roles:
        strength += 15
    if profile.github_url:
        strength += 10
    if profile.leetcode_url:
        strength += 10
    if profile.resume_url:
        strength += 20
        
    skill_contrib = min(20, skill_count * 5)
    strength += skill_contrib
    return min(100, strength)

@router.post("/initialize", response_model=ProfileOut)
async def initialize_profile(
    profile_in: ProfileInitialize,
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        profile = StudentProfile(student_id=current_user.id)
        db.add(profile)
        
    profile.bio = profile_in.bio
    profile.target_roles = profile_in.target_roles
    profile.github_url = profile_in.github_url
    profile.leetcode_url = profile_in.leetcode_url
    profile.resume_url = profile_in.resume_url
    
    skills_count_res = await db.execute(
        select(StudentSkill).where(StudentSkill.student_id == current_user.id)
    )
    skills_count = len(skills_count_res.all())
    
    profile.profile_strength = calculate_strength(profile, skills_count)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("", response_model=ProfileOut)
async def get_profile(
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.post("/skills")
async def update_skills(
    skills_in: StudentSkillsUpdate,
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    for skill_item in skills_in.skills:
        skill_res = await db.execute(
            select(SkillsMaster).where(SkillsMaster.skill_name == skill_item.skill_name)
        )
        master_skill = skill_res.scalar_one_or_none()
        if not master_skill:
            master_skill = SkillsMaster(
                skill_name=skill_item.skill_name,
                category="General"
            )
            db.add(master_skill)
            await db.flush()
            
        student_skill_res = await db.execute(
            select(StudentSkill).where(
                (StudentSkill.student_id == current_user.id) & 
                (StudentSkill.skill_id == master_skill.id)
            )
        )
        stud_skill = student_skill_res.scalar_one_or_none()
        if not stud_skill:
            stud_skill = StudentSkill(
                student_id=current_user.id,
                skill_id=master_skill.id
            )
        stud_skill.proficiency_level = skill_item.proficiency_level
        db.add(stud_skill)
        
    await db.flush()
    
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.student_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()
    
    skills_count_res = await db.execute(
        select(StudentSkill).where(StudentSkill.student_id == current_user.id)
    )
    skills_count = len(skills_count_res.all())
    
    if profile:
        profile.profile_strength = calculate_strength(profile, skills_count)
        db.add(profile)
        
    await db.commit()
    return {
        "message": "Skills updated successfully",
        "profile_strength": profile.profile_strength if profile else 0,
        "skills_added_count": len(skills_in.skills)
    }

@router.get("/skills", response_model=List[StudentSkillOut])
async def list_skills(
    current_user: Student = Depends(get_current_student),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(SkillsMaster.skill_name, SkillsMaster.category, StudentSkill.proficiency_level, StudentSkill.updated_at)
        .join(StudentSkill, StudentSkill.skill_id == SkillsMaster.id)
        .where(StudentSkill.student_id == current_user.id)
    )
    
    skills_list = []
    for row in result.all():
        skills_list.append({
            "skill_name": row[0],
            "category": row[1],
            "proficiency_level": row[2],
            "updated_at": row[3]
        })
    return skills_list
