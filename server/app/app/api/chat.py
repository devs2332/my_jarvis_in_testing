"""
Chat API endpoints — REST and WebSocket streaming.
"""

import json
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status

from server.app.dependencies import DBSession, CurrentUser
from server.app.schemas.chat import (
    ChatRequest, ChatResponse, ConversationListItem,
    ConversationDetail, MessageResponse,
)
from server.app.services.chat_service import (
    get_or_create_conversation, save_message, track_token_usage,
    check_token_budget, get_user_conversations,
    get_conversation_messages, get_usage_stats,
)
from server.app.core.security import verify_access_token
from server.app.database import async_session_factory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, user: CurrentUser, db: DBSession):
    """Send a message and get a non-streaming response."""
    # Check token budget
    sub_result = await db.execute(
        __import__("sqlalchemy").select(
            __import__("app.models.subscription", fromlist=["Subscription"]).Subscription
        ).where(
            __import__("app.models.subscription", fromlist=["Subscription"]).Subscription.user_id == user.id
        )
    )
    from server.app.models.subscription import Subscription
    from sqlalchemy import select
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = sub_result.scalar_one_or_none()
    plan = sub.plan.value if sub else "free"

    within_budget, used, limit = await check_token_budget(db, user.id, plan)
    if not within_budget:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Token limit reached ({used}/{limit}). Upgrade your plan.",
        )

    # Get or create conversation
    conv = await get_or_create_conversation(db, user.id, request.conversation_id)

    # Save user message
    await save_message(db, conv.id, "user", request.message)

    # Route to appropriate model and get AI response
    from server.ai.llm_router import route_model
    from server.ai.agent import run_agent

    model = route_model(plan, request.model_override)
    result = await run_agent(request.message, model=model, user_id=str(user.id))

    # Save assistant message
    await save_message(
        db, conv.id, "assistant", result["content"],
        model_used=model, tokens_used=result.get("total_tokens", 0),
    )

    # Track token usage
    await track_token_usage(
        db, user.id, model,
        prompt_tokens=result.get("prompt_tokens", 0),
        completion_tokens=result.get("completion_tokens", 0),
        cost_usd=result.get("cost_usd", 0.0),
        conversation_id=conv.id,
    )

    return ChatResponse(
        message=result["content"],
        conversation_id=str(conv.id),
        model_used=model,
        tokens_used=result.get("total_tokens", 0),
        cost_usd=result.get("cost_usd", 0.0),
    )


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming chat responses."""
    await websocket.accept()

    try:
        # Authenticate via first message
        auth_msg = await websocket.receive_text()
        auth_data = json.loads(auth_msg)
        token = auth_data.get("token", "")

        payload = verify_access_token(token)
        if not payload:
            await websocket.send_json({"error": "Invalid token"})
            await websocket.close(code=4001)
            return

        user_id = uuid.UUID(payload["sub"])
        plan = payload.get("plan", "free")

        await websocket.send_json({"type": "connected", "user_id": str(user_id)})

        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            user_message = msg_data.get("message", "")
            conversation_id = msg_data.get("conversation_id")

            if not user_message:
                continue

            async with async_session_factory() as db:
                # Check budget
                within_budget, used, limit = await check_token_budget(
                    db, user_id, plan,
                )
                if not within_budget:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Token limit reached ({used}/{limit})",
                    })
                    continue

                conv = await get_or_create_conversation(
                    db, user_id, conversation_id,
                )
                await save_message(db, conv.id, "user", user_message)
                await db.commit()

            # Stream response
            from server.ai.llm_router import route_model
            from server.ai.agent import stream_agent

            model = route_model(plan)

            await websocket.send_json({
                "type": "stream_start",
                "conversation_id": str(conv.id),
                "model": model,
            })

            full_response = ""
            total_tokens = 0

            async for chunk in stream_agent(
                user_message, model=model, user_id=str(user_id),
            ):
                if chunk.get("type") == "token":
                    await websocket.send_json({
                        "type": "token",
                        "content": chunk["content"],
                    })
                    full_response += chunk["content"]
                elif chunk.get("type") == "usage":
                    total_tokens = chunk.get("total_tokens", 0)

            await websocket.send_json({
                "type": "stream_end",
                "tokens_used": total_tokens,
            })

            # Persist assistant response
            async with async_session_factory() as db:
                await save_message(
                    db, conv.id, "assistant", full_response,
                    model_used=model, tokens_used=total_tokens,
                )
                await track_token_usage(
                    db, user_id, model,
                    prompt_tokens=chunk.get("prompt_tokens", 0),
                    completion_tokens=chunk.get("completion_tokens", 0),
                    cost_usd=chunk.get("cost_usd", 0.0),
                    conversation_id=conv.id,
                )
                await db.commit()

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=4000)
        except Exception:
            pass


@router.get("/conversations")
async def list_conversations(user: CurrentUser, db: DBSession):
    """List the current user's conversations."""
    convs = await get_user_conversations(db, user.id)
    return [
        ConversationListItem(
            id=str(c.id),
            title=c.title,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in convs
    ]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str, user: CurrentUser, db: DBSession
):
    """Get conversation messages."""
    messages = await get_conversation_messages(
        db, uuid.UUID(conversation_id), user.id
    )
    return [
        MessageResponse(
            id=str(m.id),
            role=m.role,
            content=m.content,
            model_used=m.model_used,
            tokens_used=m.tokens_used,
            created_at=m.created_at.isoformat(),
        )
        for m in messages
    ]


@router.get("/usage")
async def get_usage(user: CurrentUser, db: DBSession):
    """Get token usage statistics."""
    return await get_usage_stats(db, user.id)
