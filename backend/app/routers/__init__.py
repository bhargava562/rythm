from backend.app.routers.auth import router as auth_router
from backend.app.routers.profile import router as profile_router
from backend.app.routers.opportunity import router as opportunity_router
from backend.app.routers.analytics import router as analytics_router

__all__ = [
    "auth_router",
    "profile_router",
    "opportunity_router",
    "analytics_router",
]
