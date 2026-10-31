import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    SECRET_KEY: str = "dev_secret_compiler_error_tutor_2026_secure_key_32chars!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite:///./tutor.db"

    DOCKER_SANDBOX_IMAGE: str = "tutor-sandbox:latest"
    SANDBOX_TIMEOUT_SECONDS: int = 10
    SANDBOX_MAX_CONCURRENT: int = 5
    SANDBOX_MAX_CODE_BYTES: int = 65536
    SANDBOX_MAX_OUTPUT_BYTES: int = 131072

    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
