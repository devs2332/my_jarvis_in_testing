# jarvis_ai/server/routes.py
"""
API Routes — REST + WebSocket endpoints for Jarvis AI.
"""

import asyncio
import json
import logging
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

# ─── Shared state (initialized at startup) ───
_agent = None
_vector_memory = None


class ChatRequest(BaseModel):
    message: str
    stream: bool = False


class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5


# ─── Lifecycle ───

async def startup_handler():
    """Initialize core systems on server start."""
    global _agent, _vector_memory

    from core.agent import Agent
    from core.vector_memory import VectorMemory

    _vector_memory = VectorMemory()
    _agent = Agent(vector_memory=_vector_memory)

    logger.info("🚀 Jarvis AI backend started")


async def shutdown_handler():
    logger.info("👋 Jarvis AI backend shutting down")


# ─── Health ───

@router.get("/api/health")
async def health():
    return {"status": "ok", "service": "jarvis-ai", "version": "2.0.0"}


# ─── Status ───

@router.get("/api/status")
async def get_status():
    from config import LLM_PROVIDER

    vm_stats = _vector_memory.get_stats() if _vector_memory else {}
    tools_list = []
    try:
        from core.tools import ToolRegistry
        registry = ToolRegistry()
        tools_list = registry.list_tools()
    except Exception:
        pass

    return {
        "llm_provider": LLM_PROVIDER,
        "vector_memory": vm_stats,
        "tools_count": len(tools_list),
        "tools": tools_list,
        "timestamp": time.time(),
    }


# ─── Chat ───

@router.post("/api/chat")
async def chat(req: ChatRequest):
    if not _agent:
        return {"error": "Agent not initialized"}

    start = time.time()
    response = _agent.run(req.message)
    elapsed = round(time.time() - start, 2)

    # Store in vector memory
    if _vector_memory and response:
        _vector_memory.add_conversation(req.message, response)

    return {
        "message": req.message,
        "response": response,
        "elapsed_seconds": elapsed,
        "timestamp": time.time(),
    }


# ─── WebSocket Chat (streaming) ───

@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket client connected")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_message = msg.get("message", "")

            if not user_message:
                await websocket.send_json({"type": "error", "text": "Empty message"})
                continue

            await websocket.send_json({"type": "thinking", "text": "Processing..."})

            # Try streaming if agent supports it
            if hasattr(_agent, "run_stream"):
                full_response = ""
                async for token in _agent.run_stream(user_message):
                    full_response += token
                    await websocket.send_json({"type": "token", "text": token})

                await websocket.send_json({
                    "type": "complete",
                    "text": full_response,
                    "timestamp": time.time(),
                })
            else:
                # Fallback: non-streaming
                response = _agent.run(user_message)
                await websocket.send_json({
                    "type": "complete",
                    "text": response,
                    "timestamp": time.time(),
                })

            # Store in vector memory
            if _vector_memory:
                _vector_memory.add_conversation(
                    user_message,
                    full_response if hasattr(_agent, "run_stream") else response
                )

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# ─── Memory / Knowledge Base ───

@router.get("/api/memory")
async def get_memories(limit: int = 20):
    if not _vector_memory:
        return {"memories": [], "total": 0}

    recent = _vector_memory.get_recent(n=limit)
    stats = _vector_memory.get_stats()

    return {
        "memories": recent,
        "total": stats["total_documents"],
    }


@router.get("/api/memory/search")
async def search_memories(q: str, top_k: int = 5):
    if not _vector_memory:
        return {"results": [], "query": q}

    results = _vector_memory.search(q, top_k=top_k)
    return {
        "results": results,
        "query": q,
        "count": len(results),
    }


@router.get("/api/memory/stats")
async def memory_stats():
    if not _vector_memory:
        return {"error": "Vector memory not initialized"}
    return _vector_memory.get_stats()


# ─── Conversations (from JSON memory) ───

@router.get("/api/conversations")
async def get_conversations():
    try:
        from core.memory import Memory
        mem = Memory()
        history = mem.data.get("history", [])
        return {
            "conversations": history[-50:],  # last 50
            "total": len(history),
        }
    except Exception as e:
        return {"conversations": [], "error": str(e)}


# ─── Facts (key-value memory) ───

@router.get("/api/facts")
async def get_facts():
    try:
        from core.memory import Memory
        mem = Memory()
        facts = {k: v for k, v in mem.data.items() if k != "history"}
        return {"facts": facts}
    except Exception as e:
        return {"facts": {}, "error": str(e)}
