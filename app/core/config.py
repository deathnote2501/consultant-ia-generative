import os
from pydantic_settings import BaseSettings
from typing import List, Optional # Added Optional
from pydantic import HttpUrl # For BASE_URL validation

class Settings(BaseSettings):
    PROJECT_NAME: str = "Votre Repo Backend"
    PROJECT_VERSION: str = "0.1.0"

    # Base URL for constructing full links (e.g., email verification)
    # Example: BASE_URL="http://localhost:8000" or "https://yourdomain.com"
    # Note: pydantic HttpUrl will validate the URL format.
    # The default "" is not a valid HttpUrl. Using "http://localhost:8000" as a sensible default.
    BASE_URL: HttpUrl = HttpUrl(os.getenv("BASE_URL", "http://localhost:8000"))


    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:changeme@localhost:5432/votre_repo_db")

    # FastAPI Users settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey") # THIS IS INSECURE, REPLACE IT!
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Brevo Email Sender settings
    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "your_brevo_api_key_here")
    BREVO_SENDER_EMAIL: str = os.getenv("BREVO_SENDER_EMAIL", "sender@example.com")
    BREVO_SENDER_NAME: str = os.getenv("BREVO_SENDER_NAME", "My Application")


    class Config:
        case_sensitive = True
        # env_file = ".env" # Uncomment this if you want to load from a .env file

settings = Settings()
