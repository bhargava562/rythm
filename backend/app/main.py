import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.app.database import engine, Base
from backend.app.routers.auth import router as auth_router
from backend.app.routers.profile import router as profile_router
from backend.app.routers.opportunity import router as opportunity_router
from backend.app.routers.analytics import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create postgres schemas during startup for development
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Rythm API",
    description="AI-Powered Student Career Workflow Intelligence Platform Backend Services",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(opportunity_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "Rythm Backend API",
        "documentation": "/docs"
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "OK",
        "timestamp": os.getenv("CURRENT_TIME", "2026-05-29T16:25:00")
    }
