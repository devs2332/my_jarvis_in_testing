"""
Global exception handler middleware.
Catches unhandled exceptions and returns structured error responses.
"""

import logging
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catch unhandled exceptions and return JSON error responses."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException:
            raise  # Let FastAPI handle HTTP exceptions
        except Exception as exc:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"Unhandled exception [request_id={request_id}]: {exc}",
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id,
                },
            )
