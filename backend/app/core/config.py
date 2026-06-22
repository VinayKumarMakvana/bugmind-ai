from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BugMind AI"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./bugmind.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # GitHub App & API Configuration (Global)
    GITHUB_CLIENT_ID: str = ""
    GITHUB_APP_ID: str = ""
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_API_BASE_URL: str = "https://api.github.com"
    
    # System Fallback LLM Settings (Users should provide their own in DB)
    OPENAI_API_KEY: str = ""
    
    # App URLs
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Security
    SECRET_KEY: str = "super_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    class Config:
        env_file = ".env"

settings = Settings()
