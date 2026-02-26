"""
Health check and readiness endpoints.
"""

from fastapi import APIRouter
from server.app.config import get_settings

settings = get_settings()

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Liveness probe — is the app running?"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe — can the app serve requests?"""
    checks = {}

    # Check database
    try:
        from server.app.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Check Redis
    try:
        from server.app.core.redis_client import get_redis
        r = await get_redis()
        await r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }
