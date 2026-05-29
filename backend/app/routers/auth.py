import os
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
import jwt as pyjwt
from passlib.context import CryptContext
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.models.student import Student, StudentProfile
from backend.app.schemas.student import StudentRegister, StudentLogin, StudentOut, Token, PasswordResetRequest, PasswordResetConfirm

JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkeythatyoushouldchangeinproduction123456!")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter(prefix="/auth", tags=["Authentication"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_tokens(student_id: str) -> tuple[str, str]:
    access_expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_payload = {"sub": student_id, "exp": access_expire, "type": "access"}
    access_token = pyjwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    refresh_expire = datetime.utcnow() + timedelta(days=7)
    refresh_payload = {"sub": student_id, "exp": refresh_expire, "type": "refresh"}
    refresh_token = pyjwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return access_token, refresh_token

async def get_current_student(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> Student:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        student_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if student_id is None or token_type != "access":
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if student is None:
        raise credentials_exception
    return student

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(student_in: StudentRegister, db: AsyncSession = Depends(get_db)):
    existing_result = await db.execute(
        select(Student).where(Student.email == student_in.email)
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    hashed = hash_password(student_in.password)
    new_student = Student(
        full_name=student_in.full_name,
        email=student_in.email,
        password_hash=hashed,
        college_name=student_in.college_name,
        graduation_year=student_in.graduation_year,
        branch=student_in.branch
    )
    db.add(new_student)
    await db.flush()
    
    profile_skeleton = StudentProfile(
        student_id=new_student.id,
        profile_strength=10,
        target_roles=[]
    )
    db.add(profile_skeleton)
    await db.commit()
    await db.refresh(new_student)
    
    access_token, refresh_token = create_tokens(new_student.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": new_student
    }

@router.post("/login")
async def login(login_in: StudentLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Student).where(Student.email == login_in.email)
    )
    student = result.scalar_one_or_none()
    if not student or not verify_password(login_in.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    access_token, refresh_token = create_tokens(student.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# Role-Based Access Control dependency helper
def check_role(allowed_roles: list[str]):
    async def role_checker(current_user: Student = Depends(get_current_student)) -> Student:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this user role."
            )
        return current_user
    return role_checker

# Background email task simulator
def simulate_send_email(email: str, subject: str, body: str):
    print(f"\n--- [BACKGROUND TASK] SIMULATING EMAIL TO {email} ---")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("-----------------------------------------------------\n")

@router.post("/password-reset-request")
async def request_password_reset(
    req: PasswordResetRequest, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Student).where(Student.email == req.email))
    student = result.scalar_one_or_none()
    if not student:
        return {"message": "If the email is registered, a password reset link has been sent."}
        
    token = secrets.token_urlsafe(32)
    student.reset_token = token
    db.add(student)
    await db.commit()
    
    body = f"Hello {student.full_name},\n\nUse this token to reset your password: {token}\n\nRegards,\nRythm Team"
    background_tasks.add_task(
        simulate_send_email, 
        student.email, 
        "Password Reset Request - Rythm", 
        body
    )
    return {"message": "If the email is registered, a password reset link has been sent."}

@router.post("/password-reset-confirm")
async def confirm_password_reset(req: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).where(Student.reset_token == req.token))
    student = result.scalar_one_or_none()
    if not student or not req.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token."
        )
        
    student.password_hash = hash_password(req.new_password)
    student.reset_token = None
    db.add(student)
    await db.commit()
    return {"message": "Password has been successfully reset."}
