import os
from dotenv import load_dotenv

load_dotenv()


def _fix_db_url(url: str) -> str:
    """
    Normalise DATABASE_URL to always use the psycopg2 driver.
    Handles all formats Supabase / Render may provide:
      postgres://...       -> postgresql+psycopg2://...
      postgresql://...     -> postgresql+psycopg2://...
      postgresql+psycopg2://... -> unchanged
      sqlite://...         -> unchanged (local dev)
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Settings:
    APP_NAME:    str = "TripWise AI"
    VERSION:     str = "3.0.0"
    DESCRIPTION: str = "AI-Powered Travel Planning Platform"

    # Database — raw URL from env, normalised to psycopg2 scheme
    DATABASE_URL: str = _fix_db_url(
        os.getenv("DATABASE_URL", "sqlite:///./tripwise.db")
    )

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL:   str = os.getenv("GEMINI_MODEL", "models/gemini-flash-lite-latest")

    # JWT
    SECRET_KEY:                  str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM:                   str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Weather (OpenWeatherMap — optional)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")

    # Admin
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "admin-secret")

    # Rate Limiting
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", 10))


settings = Settings()
