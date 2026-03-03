"""
Application configuration using Pydantic Settings.
All config is loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Enterprise Jarvis AI Platform configuration."""

    # ── App ──────────────────────────────────────────────
    APP_NAME: str = "Enterprise Jarvis AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # development | staging | production
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ── Database ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://jarvis:jarvis_secret@localhost:5432/jarvis_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # ── Redis ────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # seconds

    # ── JWT ──────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE-ME-super-secret-jwt-key-2024"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── OpenAI ───────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    MODEL_FREE: str = "gpt-4o-mini"
    MODEL_PRO: str = "gpt-4o"
    MODEL_ENTERPRISE: str = "gpt-4o"
    MODEL_FALLBACK: str = "gpt-4o-mini"

    # ── Stripe ───────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_FREE: str = ""
    STRIPE_PRICE_PRO: str = ""
    STRIPE_PRICE_ENTERPRISE: str = ""

    # ── Rate Limiting ────────────────────────────────────
    RATE_LIMIT_FREE: int = 20        # requests per minute
    RATE_LIMIT_PRO: int = 60
    RATE_LIMIT_ENTERPRISE: int = 200

    # ── Token Limits (per billing cycle) ─────────────────
    TOKEN_LIMIT_FREE: int = 100_000
    TOKEN_LIMIT_PRO: int = 1_000_000
    TOKEN_LIMIT_ENTERPRISE: int = 10_000_000

    # ── Chroma Vector DB ─────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ── Logging ──────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
