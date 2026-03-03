from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env: prefer project root (../.env) over CWD (.env)
_this_dir = Path(__file__).resolve().parent  # backend/app/
_project_root_env = _this_dir.parent.parent / ".env"  # travel-ai/.env
_backend_env = _this_dir.parent / ".env"  # backend/.env
_env_file = str(_project_root_env) if _project_root_env.is_file() else str(_backend_env)


class Settings(BaseSettings):
    # Application
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://travelai:travelai_dev_password@db:5432/travelai"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    # Amadeus
    AMADEUS_API_KEY: str = ""
    AMADEUS_API_SECRET: str = ""
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"

    # RapidAPI
    RAPIDAPI_KEY: str = ""
    RAPIDAPI_SKYSCANNER_HOST: str = "fly-scraper.p.rapidapi.com"
    RAPIDAPI_KIWI_HOST: str = "flights-scraper-real-time.p.rapidapi.com"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@travel-ai.com"
    EMAIL_FROM_NAME: str = "Travel-AI"

    # Tier switch (dev/test only)
    ALLOW_TIER_SWITCH: bool = False

    @property
    def is_development(self) -> bool:
        return self.ENV in ("development", "test")

    model_config = {"env_file": _env_file, "extra": "ignore"}


settings = Settings()
