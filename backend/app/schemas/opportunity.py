from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class ApplicationIngest(BaseModel):
    company_name: str
    role: str
    source_platform: str
    application_url: Optional[str] = None
    deadline: date
    job_description_text: str

class ApplicationRequiredSkillOut(BaseModel):
    skill_name: str
    category: str

    class Config:
        from_attributes = True

class ApplicationAIAnalysis(BaseModel):
    extracted_domain: str
    extracted_experience_level: str
    required_skills: List[str]
    match_score: float
    matching_skills: List[str]
    missing_skills: List[str]

class ApplicationIngestOut(BaseModel):
    id: str
    company_name: str
    role: str
    status: str
    priority_score: float
    ai_analysis: ApplicationAIAnalysis

    class Config:
        from_attributes = True

class ApplicationOut(BaseModel):
    id: str
    company_name: str
    role: str
    deadline: date
    status: str
    priority_score: float
    created_at: datetime

    class Config:
        from_attributes = True

class ApplicationStatusTransition(BaseModel):
    new_status: str
    notes: Optional[str] = None

class ApplicationStatusHistoryOut(BaseModel):
    old_status: str
    new_status: str
    notes: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True

class ResumeTailorRequest(BaseModel):
    raw_resume_text: str

class SuggestedResumeChange(BaseModel):
    original: str
    replacement: str

class ResumeTailorResponse(BaseModel):
    application_id: str
    target_role: str
    matching_score_estimate: float
    suggestions: dict
