"""
Authentication service — handles user registration, login, and token refresh.
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from server.app.models.user import User
from server.app.models.subscription import Subscription, PlanType, SubscriptionStatus
from server.app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from server.app.core.audit_log import audit_log


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


async def register_user(
    db: AsyncSession, email: str, password: str, full_name: str = None
) -> tuple[User, str, str]:
    """
    Register a new user.
    Returns (user, access_token, refresh_token).
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        raise AuthenticationError("Email already registered")

    # Create user
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        api_key=f"jrv_{uuid.uuid4().hex}",
    )
    db.add(user)
    await db.flush()

    # Create free subscription
    subscription = Subscription(
        user_id=user.id,
        plan=PlanType.FREE,
        status=SubscriptionStatus.ACTIVE,
    )
    db.add(subscription)
    await db.flush()

    # Generate tokens
    access_token = create_access_token(user.id, role=user.role.value)
    refresh_token = create_refresh_token(user.id)

    audit_log("user_registered", user_id=str(user.id), resource="auth")
    return user, access_token, refresh_token


async def login_user(
    db: AsyncSession, email: str, password: str
) -> tuple[User, str, str]:
    """
    Authenticate a user and return tokens.
    Raises AuthenticationError on failure.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        audit_log("login_failed", resource="auth", detail={"email": email}, status="failure")
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is deactivated")

    access_token = create_access_token(user.id, role=user.role.value)
    refresh_token = create_refresh_token(user.id)

    audit_log("user_login", user_id=str(user.id), resource="auth")
    return user, access_token, refresh_token


async def refresh_tokens(
    db: AsyncSession, user_id: uuid.UUID
) -> tuple[str, str]:
    """Generate new access and refresh tokens for a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    access_token = create_access_token(user.id, role=user.role.value)
    refresh_token = create_refresh_token(user.id)
    return access_token, refresh_token
