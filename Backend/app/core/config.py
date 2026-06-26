import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = "TripWise AI"
    VERSION: str = "3.0.0"
    DESCRIPTION: str = "AI-Powered Travel Planning Platform"

    # Database
    _DB_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tripwise.db")
    if _DB_URL.startswith("postgresql://"):
        DATABASE_URL: str = _DB_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
    else:
        DATABASE_URL: str = _DB_URL

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Weather API (optional — plug in OpenWeatherMap key)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Firebase
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")

    # Admin
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "admin-secret")

    # Rate Limiting
    AI_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AI_RATE_LIMIT_PER_MINUTE", 10))


settings = Settings()
