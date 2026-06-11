from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Tripwise API"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./tripwise.db"

    # OpenAI
    OPENAI_API_KEY: str

    # JWT Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
