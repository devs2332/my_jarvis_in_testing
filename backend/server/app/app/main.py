"""
Enterprise Jarvis AI Platform — FastAPI Application Entry Point.

Production-ready with full middleware stack, structured logging,
and proper lifecycle management.
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.server.app.config import get_settings
from backend.server.app.database import init_db, close_db
from backend.server.app.core.redis_client import get_redis, close_redis
from backend.server.app.middleware.rate_limiter import RateLimitMiddleware
from backend.server.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.server.app.middleware.logging_middleware import LoggingMiddleware
from backend.server.app.middleware.error_handler import ErrorHandlerMiddleware

from backend.server.app.api.auth import router as auth_router
from backend.server.app.api.chat import router as chat_router
from backend.server.app.api.billing import router as billing_router
from backend.server.app.api.admin import router as admin_router
from backend.server.app.api.health import router as health_router
from backend.server.app.api.metrics import router as metrics_router

settings = get_settings()


# ── Structured Logging Setup ────────────────────────────

def setup_logging():
    """Configure structured JSON logging."""
    log_format = (
        '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        if settings.LOG_FORMAT == "json"
        else "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        stream=sys.stdout,
    )


setup_logging()
logger = logging.getLogger(__name__)


# ── Application Lifespan ────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and teardown application resources."""
    logger.info("🚀 Starting Enterprise Jarvis AI Platform")

    # Initialize database tables (dev only — use Alembic in prod)
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize Redis
    await get_redis()
    logger.info("✅ Redis connected")

    yield  # App is running

    # Shutdown
    await close_redis()
    await close_db()
    logger.info("👋 Enterprise Jarvis AI Platform shut down")


# ── Create FastAPI Application ──────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade AI Assistant SaaS Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# ── Middleware Stack (order matters — outermost first) ───

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
)


# ── Register Routers ────────────────────────────────────

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(billing_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(health_router)
app.include_router(metrics_router)


# ── Root Endpoint ────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }
