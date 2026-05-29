from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class StudentRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    college_name: str
    graduation_year: int
    branch: str

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class StudentOut(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    college_name: str
    graduation_year: int
    branch: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: StudentOut

class TokenData(BaseModel):
    student_id: Optional[str] = None

class ProfileInitialize(BaseModel):
    bio: Optional[str] = None
    target_roles: List[str]
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    resume_url: Optional[str] = None

class ProfileOut(BaseModel):
    student_id: str
    bio: Optional[str] = None
    target_roles: List[str]
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    resume_url: Optional[str] = None
    profile_strength: int
    updated_at: datetime

    class Config:
        from_attributes = True
