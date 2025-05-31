import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Votre Repo Backend"
    PROJECT_VERSION: str = "0.1.0"

    # Database settings
    # The default value assumes a local PostgreSQL instance.
    # Replace with your actual database URL, potentially loaded from environment variables.
    # Example: DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:changeme@localhost:5432/votre_repo_db")

    # FastAPI Users settings
    # Generate a real secret key, e.g., using: openssl rand -hex 32
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "supersecretkey") # THIS IS INSECURE, REPLACE IT!
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7     # 7 days

    # CORS settings (optional, but good to have)
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"] # Example for a React frontend

    class Config:
        case_sensitive = True
        # env_file = ".env" # Uncomment this if you want to load from a .env file

settings = Settings()
