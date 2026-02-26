"""
JWT authentication and password hashing utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from server.app.config import get_settings

settings = get_settings()

# ── Password Hashing ────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ──────────────────────────────────────────

def create_access_token(
    subject: str | uuid.UUID,
    role: str = "user",
    extra: Optional[dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | uuid.UUID) -> str:
    """Create a signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.
    Raises JWTError on invalid/expired tokens.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def verify_access_token(token: str) -> Optional[dict[str, Any]]:
    """Verify an access token and return the payload, or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[dict[str, Any]]:
    """Verify a refresh token and return the payload, or None."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
