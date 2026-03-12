# jarvis_ai/server/schemas.py
"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any


class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    research_mode: bool = False
    fast_mode: bool = False
    search_mode: str = "none"  # 'none' | 'web_search' | 'deep_research'
    language: str = "English"
    provider: Optional[str] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    response: str
    research_mode: bool = False
    elapsed_seconds: float = 0.0
    timestamp: float = 0.0


class ToolCallRequest(BaseModel):
    tool_name: str
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    tool_name: str
    result: Any
    success: bool
    error: Optional[str] = None


class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5


class StatusResponse(BaseModel):
    llm_provider: str
    vector_memory: dict = Field(default_factory=dict)
    tools_count: int = 0
    tools: list[str] = Field(default_factory=list)
    timestamp: float = 0.0


class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: dict = Field(default_factory=dict)
