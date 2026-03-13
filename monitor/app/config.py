from pydantic_settings import BaseSettings


class MonitorSettings(BaseSettings):
    ENV: str = "development"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://travelai:travelai_dev_password@db:5432/travelai"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Amadeus
    AMADEUS_API_KEY: str = ""
    AMADEUS_API_SECRET: str = ""
    AMADEUS_BASE_URL: str = "https://test.api.amadeus.com"

    # RapidAPI (Skyscanner + Kiwi)
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

    # Monitoring
    SCAN_INTERVAL_HOURS: int = 4
    BUG_FARE_THRESHOLD: float = 0.5  # 50% below average
    MAX_ROUTES_STANDARD: int = 55
    MAX_ROUTES_REDUCED: int = 100

    SECRET_KEY: str = "change-me-in-production"
    BACKEND_URL: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = MonitorSettings()
