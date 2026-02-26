"""
User service — user management operations.
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from server.app.models.user import User, UserRole


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user: User,
    full_name: str = None,
    email: str = None,
) -> User:
    """Update user profile fields."""
    if full_name is not None:
        user.full_name = full_name
    if email is not None:
        # Check uniqueness
        existing = await get_user_by_email(db, email)
        if existing and existing.id != user.id:
            raise ValueError("Email already in use")
        user.email = email
    await db.flush()
    return user


async def list_users(
    db: AsyncSession, page: int = 1, per_page: int = 20
) -> tuple[list[User], int]:
    """List users with pagination (admin only)."""
    offset = (page - 1) * per_page

    result = await db.execute(
        select(User).offset(offset).limit(per_page).order_by(User.created_at.desc())
    )
    users = list(result.scalars().all())

    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar()

    return users, total


async def update_user_role(
    db: AsyncSession, user_id: uuid.UUID, role: str
) -> User:
    """Update a user's role (admin only)."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    user.role = UserRole(role)
    await db.flush()
    return user


async def deactivate_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    """Deactivate a user account (admin only)."""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValueError("User not found")

    user.is_active = False
    await db.flush()
    return user
