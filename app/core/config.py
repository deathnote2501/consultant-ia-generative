import os
from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import HttpUrl, EmailStr # EmailStr for BREVO_SENDER_EMAIL

class Settings(BaseSettings):
    PROJECT_NAME: str = "Votre Repo Backend"
    PROJECT_VERSION: str = "0.1.0"

    # Base URL for constructing full links (e.g., email verification)
    # Example: BASE_URL="http://localhost:8000" or "https://yourdomain.com"
    # Note: pydantic HttpUrl will validate the URL format.
    BASE_URL: HttpUrl = HttpUrl(os.getenv("BASE_URL", "http://localhost:8000"))

    # Frontend URL (for constructing callback URLs, etc.)
    # Example: FRONTEND_URL="http://localhost:5173" for a SvelteKit/React app
    FRONTEND_URL: HttpUrl = HttpUrl(os.getenv("FRONTEND_URL", "http://localhost:5173"))


    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:changeme@localhost:5432/votre_repo_db")

    # FastAPI Users settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey") # THIS IS INSECURE, REPLACE IT!
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS settings - add frontend dev default
    BACKEND_CORS_ORIGINS: List[str] = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")


    # Brevo Email Sender settings
    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "your_brevo_api_key_here") # Replace with actual or ensure env var is set
    BREVO_SENDER_EMAIL: EmailStr = EmailStr(os.getenv("BREVO_SENDER_EMAIL", "sender@example.com"))
    BREVO_SENDER_NAME: str = os.getenv("BREVO_SENDER_NAME", "My Application")

    # Stripe Settings
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_yourstripenetkeyhere") # Replace with actual or ensure env var is set
    # STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY", None) # Optional, not used in this task
    # STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET", None) # Optional, for webhook verification later


    class Config:
        case_sensitive = True
        # env_file = ".env" # Uncomment this if you want to load from a .env file
        # extra = 'ignore' # To ignore extra fields from .env if any

settings = Settings()
