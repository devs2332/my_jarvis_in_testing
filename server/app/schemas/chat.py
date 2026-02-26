"""Pydantic schemas for chat system."""

from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[str] = None
    model_override: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    model_used: str
    tokens_used: int
    cost_usd: float


class ConversationListItem(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int = 0

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    model_used: str | None
    tokens_used: int | None
    created_at: str

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[MessageResponse]
