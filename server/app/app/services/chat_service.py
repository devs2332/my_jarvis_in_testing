"""
Chat service — orchestrates AI agent, conversation persistence, and token tracking.
"""

import uuid
import logging
from typing import AsyncGenerator, Optional
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from server.app.models.conversation import Conversation, Message
from server.app.models.token_usage import TokenUsage
from server.app.models.subscription import Subscription
from server.app.models.user import User
from server.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

TOKEN_LIMITS = {
    "free": settings.TOKEN_LIMIT_FREE,
    "pro": settings.TOKEN_LIMIT_PRO,
    "enterprise": settings.TOKEN_LIMIT_ENTERPRISE,
}


async def get_or_create_conversation(
    db: AsyncSession, user_id: uuid.UUID, conversation_id: Optional[str] = None
) -> Conversation:
    """Get existing or create a new conversation."""
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == uuid.UUID(conversation_id),
                Conversation.user_id == user_id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    conv = Conversation(user_id=user_id)
    db.add(conv)
    await db.flush()
    return conv


async def save_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    model_used: Optional[str] = None,
    tokens_used: Optional[int] = None,
) -> Message:
    """Save a message to a conversation."""
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        model_used=model_used,
        tokens_used=tokens_used,
    )
    db.add(msg)
    await db.flush()
    return msg


async def track_token_usage(
    db: AsyncSession,
    user_id: uuid.UUID,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    conversation_id: Optional[uuid.UUID] = None,
) -> TokenUsage:
    """Record token usage for billing."""
    usage = TokenUsage(
        user_id=user_id,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
        cost_usd=cost_usd,
        conversation_id=conversation_id,
    )
    db.add(usage)
    await db.flush()
    return usage


async def check_token_budget(
    db: AsyncSession, user_id: uuid.UUID, plan: str
) -> tuple[bool, int, int]:
    """
    Check if the user is within their token budget.
    Returns (within_budget, used, limit).
    """
    limit = TOKEN_LIMITS.get(plan, TOKEN_LIMITS["free"])

    result = await db.execute(
        select(func.coalesce(func.sum(TokenUsage.total_tokens), 0)).where(
            TokenUsage.user_id == user_id
        )
    )
    used = result.scalar()

    return used < limit, used, limit


async def get_user_conversations(
    db: AsyncSession, user_id: uuid.UUID, limit: int = 50
) -> list[Conversation]:
    """Get a user's conversations, most recent first."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_conversation_messages(
    db: AsyncSession, conversation_id: uuid.UUID, user_id: uuid.UUID
) -> list[Message]:
    """Get messages for a conversation (ensures user ownership)."""
    # Verify ownership
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        return []

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())


async def get_usage_stats(
    db: AsyncSession, user_id: uuid.UUID
) -> dict:
    """Get token usage statistics for a user."""
    # Total usage
    result = await db.execute(
        select(
            func.coalesce(func.sum(TokenUsage.total_tokens), 0),
            func.coalesce(func.sum(TokenUsage.cost_usd), 0),
        ).where(TokenUsage.user_id == user_id)
    )
    total_tokens, total_cost = result.one()

    # Per-model breakdown
    result = await db.execute(
        select(
            TokenUsage.model,
            func.sum(TokenUsage.total_tokens),
            func.sum(TokenUsage.cost_usd),
        )
        .where(TokenUsage.user_id == user_id)
        .group_by(TokenUsage.model)
    )
    breakdown = {
        row[0]: {"tokens": int(row[1]), "cost_usd": float(row[2])}
        for row in result.all()
    }

    # Get plan limit
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    sub = sub_result.scalar_one_or_none()
    plan = sub.plan.value if sub else "free"
    limit = TOKEN_LIMITS.get(plan, TOKEN_LIMITS["free"])

    return {
        "total_tokens": int(total_tokens),
        "total_cost_usd": float(total_cost),
        "token_limit": limit,
        "usage_percentage": round((int(total_tokens) / limit) * 100, 2) if limit > 0 else 0,
        "breakdown_by_model": breakdown,
    }
