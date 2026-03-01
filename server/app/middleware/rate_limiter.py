"""
Redis-backed rate limiting middleware.
Per-user limits based on subscription plan.
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from server.app.core.security import verify_access_token
from server.app.core.redis_client import check_rate_limit
from server.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Plan → requests per minute
PLAN_LIMITS = {
    "free": settings.RATE_LIMIT_FREE,
    "pro": settings.RATE_LIMIT_PRO,
    "enterprise": settings.RATE_LIMIT_ENTERPRISE,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter using Redis sorted sets."""

    EXEMPT_PATHS = {"/health", "/ready", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health/docs routes
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Extract user identity from JWT
        auth_header = request.headers.get("Authorization", "")
        token = request.query_params.get("token", "")
        user_id = "anonymous"
        plan = "free"

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        if token:
            payload = verify_access_token(token)
            if payload:
                user_id = payload.get("sub", "anonymous")
                plan = payload.get("plan", "free")

        limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        allowed, remaining = await check_rate_limit(user_id, limit)

        if not allowed:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
