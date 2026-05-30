import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv

load_dotenv()

from backend.app.database import engine, Base
from backend.app.routers.auth import router as auth_router
from backend.app.routers.profile import router as profile_router
from backend.app.routers.opportunity import router as opportunity_router
from backend.app.routers.analytics import router as analytics_router

# Sliding Window Rate Limiter Settings
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 60 # 60 requests per minute limit
request_history = {}

async def rate_limiter(request: Request):
    """Global sliding window rate limiting dependency."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Exclude Swagger and healthcheck from rate limits for developer convenience
    path = request.url.path
    if path in ["/", "/docs", "/openapi.json", "/redoc", "/api/v1/health"]:
        return

    now = time.time()
    history = request_history.get(client_ip, [])
    
    # Filter out historical timestamps older than window
    history = [t for t in history if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    if len(history) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again after 60 seconds."
        )
    
    history.append(now)
    request_history[client_ip] = history

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup in local development
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="Rythm API",
    description="AI-Powered Student Career Workflow Intelligence Platform Backend Services",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(rate_limiter)] # Globally protect all routes
)

# Enable GZip response compression for responses larger than 1000 bytes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under api namespace
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
        "timestamp": os.getenv("CURRENT_TIME", "2026-05-30T17:15:00")
    }
