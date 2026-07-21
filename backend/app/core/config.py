from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =====================================================
    # APP
    # =====================================================

    PROJECT_NAME: str = "BugMind AI"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL: str = "mongodb://localhost:27017/bugmind"

    # =====================================================
    # REDIS
    # =====================================================

    REDIS_URL: str = "redis://localhost:6379/0"

    # =====================================================
    # GITHUB
    # =====================================================

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    GITHUB_APP_ID: str = ""
    GITHUB_APP_PRIVATE_KEY: str = ""

    GITHUB_WEBHOOK_SECRET: str = ""

    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # =====================================================
    # GOOGLE OAUTH
    # =====================================================

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # =====================================================
    # OPENAI
    # =====================================================

    OPENAI_API_KEY: str = ""

    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    OPENAI_BASE_URL: str = ""

    OPENAI_TEMPERATURE: float = 0.2

    OPENAI_MAX_CONTEXT: int = 12000

    OPENAI_MAX_CODE: int = 50000

    # =====================================================
    # CHROMADB
    # =====================================================

    CHROMA_DB_PATH: str = "./chroma_db"

    CHROMA_COLLECTION: str = "bugmind_code_chunks"

    # =====================================================
    # APP URL
    # =====================================================

    FRONTEND_URL: str = "http://localhost:3000"

    # =====================================================
    # SECURITY
    # =====================================================

    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # =====================================================
    # ANALYSIS
    # =====================================================

    STATIC_ANALYSIS_TIMEOUT: int = 300

    MAX_STATIC_FINDINGS: int = 1000

    RAG_TOP_K: int = 5

    REVIEW_MAX_RETRIES: int = 3

    # =====================================================
    # CELERY
    # =====================================================

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"

    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # =====================================================
    # PYDANTIC SETTINGS
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()