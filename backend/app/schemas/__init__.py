from backend.app.schemas.student import StudentRegister, StudentLogin, StudentOut, Token, TokenData, ProfileInitialize, ProfileOut, PasswordResetRequest, PasswordResetConfirm
from backend.app.schemas.skill import SkillMasterBase, SkillMasterOut, StudentSkillAdd, StudentSkillsUpdate, StudentSkillOut, SkillTrendOut
from backend.app.schemas.opportunity import (
    ApplicationIngest,
    ApplicationAIAnalysis,
    ApplicationIngestOut,
    ApplicationOut,
    ApplicationStatusTransition,
    ApplicationStatusHistoryOut,
    ResumeTailorRequest,
    ResumeTailorResponse
)

__all__ = [
    "StudentRegister",
    "StudentLogin",
    "StudentOut",
    "Token",
    "TokenData",
    "ProfileInitialize",
    "ProfileOut",
    "SkillMasterBase",
    "SkillMasterOut",
    "StudentSkillAdd",
    "StudentSkillsUpdate",
    "StudentSkillOut",
    "SkillTrendOut",
    "ApplicationIngest",
    "ApplicationAIAnalysis",
    "ApplicationIngestOut",
    "ApplicationOut",
    "ApplicationStatusTransition",
    "ApplicationStatusHistoryOut",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "ResumeTailorRequest",
    "ResumeTailorResponse",
]
