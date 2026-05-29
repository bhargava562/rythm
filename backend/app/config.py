from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Rythm - Career Workflow Platform"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rythm"
    
    JWT_SECRET: str = "supersecretkeythatyoushouldchangeinproduction123456!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    OPENAI_API_KEY: str = "sk-proj-..."
    GEMINI_API_KEY: str = "AIzaSy..."

    WEIGHT_URGENCY: float = 0.30
    WEIGHT_SKILL_MATCH: float = 0.40
    WEIGHT_TREND_RELEVANCE: float = 0.15
    WEIGHT_STUDENT_INTEREST: float = 0.15

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
