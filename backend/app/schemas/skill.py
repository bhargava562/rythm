from pydantic import BaseModel
from typing import List
from datetime import datetime, date

class SkillMasterBase(BaseModel):
    skill_name: str
    category: str

class SkillMasterOut(SkillMasterBase):
    id: str

    class Config:
        from_attributes = True

class StudentSkillAdd(BaseModel):
    skill_name: str
    proficiency_level: str

class StudentSkillsUpdate(BaseModel):
    skills: List[StudentSkillAdd]

class StudentSkillOut(BaseModel):
    skill_name: str
    category: str
    proficiency_level: str
    updated_at: datetime

    class Config:
        from_attributes = True

class SkillTrendOut(BaseModel):
    skill_name: str
    demand_count: int
    trend_percentage: float
    measured_date: date

    class Config:
        from_attributes = True
