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
    research_mode: bool = False
    fast_mode: bool = False
    language: str = "English"
    provider: Optional[str] = None
    model: Optional[str] = None


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
    response = _agent.run(req.message, research_mode=req.research_mode, fast_mode=req.fast_mode, language=req.language, provider=req.provider, model=req.model)
    elapsed = round(time.time() - start, 2)

    # Store in vector memory
    if _vector_memory and response:
        _vector_memory.add_conversation(req.message, response)

    return {
        "message": req.message,
        "response": response,
        "research_mode": req.research_mode,
        "elapsed_seconds": elapsed,
        "timestamp": time.time(),
    }

# ...

@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket client connected (Chat)")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_message = msg.get("message", "")
            research_mode = msg.get("research_mode", False)
            fast_mode = msg.get("fast_mode", False)
            language = msg.get("language", "English")
            provider = msg.get("provider", None)
            model = msg.get("model", None)

            if not user_message:
                await websocket.send_json({"type": "error", "text": "Empty message"})
                continue

            await websocket.send_json({"type": "thinking", "text": "Processing..."})

            # Try streaming if agent supports it
            if hasattr(_agent, "run_stream"):
                full_response = ""
                async for token in _agent.run_stream(user_message, research_mode=research_mode, fast_mode=fast_mode, language=language, provider=provider, model=model):
                    full_response += token
                    await websocket.send_json({"type": "token", "text": token})

                await websocket.send_json({
                    "type": "complete",
                    "text": full_response,
                    "timestamp": time.time(),
                })
            else:
                # Fallback: non-streaming
                response = _agent.run(user_message, research_mode=research_mode, fast_mode=fast_mode, language=language, provider=provider, model=model)
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
        logger.info("🔌 WebSocket client disconnected (Chat)")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@router.websocket("/ws")
async def ws_status(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket client connected (Status)")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "get_status":
                from config import LLM_PROVIDER
                vm_stats = _vector_memory.get_stats() if _vector_memory else {}
                
                status_payload = {
                    "type": "status_update",
                    "payload": {
                        "llm_provider": LLM_PROVIDER,
                        "vector_memory": vm_stats,
                        "timestamp": time.time(),
                        "connected": True
                    }
                }
                await websocket.send_json(status_payload)
            else:
                # Keep alive / ping
                await websocket.send_json({"type": "pong", "timestamp": time.time()})

            # Optional: could push periodic updates here if we wanted
            
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected (Status)")
    except Exception as e:
        logger.error(f"Status WebSocket error: {e}")


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


# ─── History & Trash (JSON Memory) ───

@router.get("/api/history")
async def get_history(limit: int = 50):
    try:
        from core.memory import Memory
        mem = Memory()
        history = mem.get_history(limit=limit)
        return {"conversations": history}
    except Exception as e:
        return {"conversations": [], "error": str(e)}

@router.delete("/api/history/{item_id}")
async def delete_history_item(item_id: str):
    try:
        from core.memory import Memory
        mem = Memory()
        success = mem.move_to_trash(item_id)
        if success:
            return {"status": "success", "message": "Moved to trash"}
        return {"status": "error", "message": "Item not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/trash")
async def get_trash():
    try:
        from core.memory import Memory
        mem = Memory()
        trash = mem.get_trash()
        return {"trash": trash}
    except Exception as e:
        return {"trash": [], "error": str(e)}

@router.post("/api/trash/{item_id}/restore")
async def restore_trash_item(item_id: str):
    try:
        from core.memory import Memory
        mem = Memory()
        success = mem.restore_from_trash(item_id)
        if success:
            return {"status": "success", "message": "Restored from trash"}
        return {"status": "error", "message": "Item not found in trash"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.delete("/api/trash/empty")
async def empty_trash():
    try:
        from core.memory import Memory
        mem = Memory()
        mem.empty_trash()
        return {"status": "success", "message": "Trash emptied"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.delete("/api/trash/{item_id}")
async def delete_trash_item(item_id: str):
    try:
        from core.memory import Memory
        mem = Memory()
        success = mem.delete_permanently(item_id)
        if success:
            return {"status": "success", "message": "Deleted permanently"}
        return {"status": "error", "message": "Item not found in trash"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/api/facts")
async def get_facts():
    try:
        from core.memory import Memory
        mem = Memory()
        facts = {k: v for k, v in mem.data.items() if k not in ["history", "trash"]}
        return {"facts": facts}
    except Exception as e:
        return {"facts": {}, "error": str(e)}
