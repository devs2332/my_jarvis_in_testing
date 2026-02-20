# jarvis_ai/server/routes.py
"""
API Routes — REST + WebSocket endpoints for Jarvis AI.

All shared state (agent, memory, vector_memory, voice_manager) is accessed
via request.app.state, initialized in app.py lifespan.
"""

import asyncio
import json
import logging
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from server.schemas import ChatRequest, ChatResponse, ToolCallRequest, ToolCallResponse, ToolSchema

logger = logging.getLogger(__name__)

router = APIRouter()


# ─── Helpers to access shared state ───

def _agent(request: Request):
    return request.app.state.agent

def _vector_memory(request: Request):
    return request.app.state.vector_memory

def _memory(request: Request):
    return request.app.state.memory

def _voice_manager(request: Request):
    return request.app.state.voice_manager


# ─── Health ───

@router.get("/api/health")
async def health():
    return {"status": "ok", "service": "jarvis-ai", "version": "3.0.0"}


# ─── Status ───

@router.get("/api/status")
async def get_status(request: Request):
    from config import LLM_PROVIDER

    vm = _vector_memory(request)
    vm_stats = vm.get_stats() if vm else {}
    
    tools_list = []
    try:
        agent = _agent(request)
        if agent and agent.tool_registry:
            tools_list = agent.tool_registry.list_tools()
    except Exception:
        pass

    return {
        "llm_provider": LLM_PROVIDER,
        "vector_memory": vm_stats,
        "tools_count": len(tools_list),
        "tools": tools_list,
        "timestamp": time.time(),
    }


# ─── Chat (REST) ───

@router.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    agent = _agent(request)
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    start = time.time()
    response = agent.run(
        req.message,
        research_mode=req.research_mode,
        fast_mode=req.fast_mode,
        language=req.language,
        provider=req.provider,
        model=req.model,
    )
    elapsed = round(time.time() - start, 2)

    # Store in vector memory (single point of storage)
    vm = _vector_memory(request)
    if vm and response:
        vm.add_conversation(req.message, response)

    return {
        "message": req.message,
        "response": response,
        "research_mode": req.research_mode,
        "elapsed_seconds": elapsed,
        "timestamp": time.time(),
    }


# ─── Chat (WebSocket Streaming) ───

@router.websocket("/ws/chat")
async def ws_chat(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket client connected (Chat)")

    app = websocket.app
    agent = app.state.agent
    vm = app.state.vector_memory
    voice = app.state.voice_manager

    # Voice callback — fires when STT recognizes speech
    def on_speech_recognized(text):
        if not text:
            return
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    _process_voice_command(text, websocket, agent, vm, voice),
                    loop,
                )
        except Exception as e:
            logger.error(f"Voice callback err: {e}")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            # 1) Voice Toggle
            if msg.get("type") == "voice_toggle":
                if msg.get("active"):
                    voice.start(on_speech_recognized_callback=on_speech_recognized)
                    await websocket.send_json({"type": "info", "text": "Microphone armed."})
                else:
                    voice.stop()
                    await websocket.send_json({"type": "info", "text": "Microphone disarmed."})
                continue

            # 2) Regular Text Chat
            user_message = msg.get("message", "")
            research_mode = msg.get("research_mode", False)
            fast_mode = msg.get("fast_mode", False)
            language = msg.get("language", "English")
            provider = msg.get("provider", None)
            model = msg.get("model", None)

            if not user_message:
                await websocket.send_json({"type": "error", "text": "Empty message"})
                continue

            await _process_chat_message(
                user_message, websocket, agent, vm, voice,
                research_mode, fast_mode, language, provider, model,
            )

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected (Chat)")
        voice.stop()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        voice.stop()


async def _process_voice_command(text, websocket, agent, vm, voice):
    """Callback fired by VoiceManager when STT finishes processing an utterance."""
    await websocket.send_json({"type": "user_voice_echo", "text": text, "timestamp": time.time()})
    await _process_chat_message(text, websocket, agent, vm, voice, False, False, "English", None, None)


async def _process_chat_message(user_message, websocket, agent, vm, voice,
                                research_mode, fast_mode, language, provider, model):
    """Shared core logic for handling an LLM request and streaming back over WS."""
    await websocket.send_json({"type": "thinking", "text": "Processing..."})

    full_response = ""

    if hasattr(agent, "run_stream"):
        async for token in agent.run_stream(
            user_message,
            research_mode=research_mode,
            fast_mode=fast_mode,
            language=language,
            provider=provider,
            model=model,
        ):
            full_response += token
            await websocket.send_json({"type": "token", "text": token})
    else:
        full_response = agent.run(
            user_message,
            research_mode=research_mode,
            fast_mode=fast_mode,
            language=language,
            provider=provider,
            model=model,
        )

    await websocket.send_json({
        "type": "complete",
        "text": full_response,
        "timestamp": time.time(),
    })

    # Speak response aloud if voice is active
    if voice and voice.is_listening:
        if hasattr(voice.tts, "speak_async"):
            await voice.tts.speak_async(full_response)
        else:
            voice.speak(full_response)

    # Store in vector memory (single point of storage)
    if vm:
        vm.add_conversation(user_message, full_response)


# ─── Status WebSocket ───

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
                vm = websocket.app.state.vector_memory
                vm_stats = vm.get_stats() if vm else {}

                await websocket.send_json({
                    "type": "status_update",
                    "payload": {
                        "llm_provider": LLM_PROVIDER,
                        "vector_memory": vm_stats,
                        "timestamp": time.time(),
                        "connected": True,
                    },
                })
            else:
                await websocket.send_json({"type": "pong", "timestamp": time.time()})

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket client disconnected (Status)")
    except Exception as e:
        logger.error(f"Status WebSocket error: {e}")


# ─── Memory / Knowledge Base ───

@router.get("/api/memory")
async def get_memories(request: Request, limit: int = 20):
    vm = _vector_memory(request)
    if not vm:
        return {"memories": [], "total": 0}

    recent = vm.get_recent(n=limit)
    stats = vm.get_stats()
    return {"memories": recent, "total": stats["total_documents"]}


@router.get("/api/memory/search")
async def search_memories(request: Request, q: str, top_k: int = 5):
    vm = _vector_memory(request)
    if not vm:
        return {"results": [], "query": q}

    results = vm.search(q, top_k=top_k)
    return {"results": results, "query": q, "count": len(results)}


@router.get("/api/memory/stats")
async def memory_stats(request: Request):
    vm = _vector_memory(request)
    if not vm:
        raise HTTPException(status_code=503, detail="Vector memory not initialized")
    return vm.get_stats()


# ─── History & Trash (uses shared Memory instance) ───

@router.get("/api/history")
async def get_history(request: Request, limit: int = 50):
    mem = _memory(request)
    history = mem.get_history(limit=limit)
    return {"conversations": history}


@router.delete("/api/history/{item_id}")
async def delete_history_item(item_id: str, request: Request):
    mem = _memory(request)
    success = mem.move_to_trash(item_id)
    if success:
        return {"status": "success", "message": "Moved to trash"}
    raise HTTPException(status_code=404, detail="Item not found")


@router.get("/api/trash")
async def get_trash(request: Request):
    mem = _memory(request)
    return {"trash": mem.get_trash()}


@router.post("/api/trash/{item_id}/restore")
async def restore_trash_item(item_id: str, request: Request):
    mem = _memory(request)
    success = mem.restore_from_trash(item_id)
    if success:
        return {"status": "success", "message": "Restored from trash"}
    raise HTTPException(status_code=404, detail="Item not found in trash")


@router.delete("/api/trash/empty")
async def empty_trash(request: Request):
    mem = _memory(request)
    mem.empty_trash()
    return {"status": "success", "message": "Trash emptied"}


@router.delete("/api/trash/{item_id}")
async def delete_trash_item(item_id: str, request: Request):
    mem = _memory(request)
    success = mem.delete_permanently(item_id)
    if success:
        return {"status": "success", "message": "Deleted permanently"}
    raise HTTPException(status_code=404, detail="Item not found in trash")


@router.get("/api/facts")
async def get_facts(request: Request):
    mem = _memory(request)
    facts = {k: v for k, v in mem.data.items() if k not in ["history", "trash"]}
    return {"facts": facts}


# ─── Tools ───

@router.get("/api/tools")
async def list_tools(request: Request):
    """List all registered tools with their schemas."""
    agent = _agent(request)
    if not agent or not agent.tool_registry:
        return {"tools": []}

    tools = []
    for name, meta in agent.tool_registry.tools.items():
        tools.append({
            "name": name,
            "description": meta["description"],
            "parameters": meta["parameters"],
        })
    return {"tools": tools}


@router.post("/api/tools/execute")
async def execute_tool(req: ToolCallRequest, request: Request):
    """Execute a registered tool by name with arguments."""
    agent = _agent(request)
    if not agent or not agent.tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not initialized")

    tool = agent.tool_registry.get_tool(req.tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{req.tool_name}' not found")

    try:
        result = agent.tool_registry.execute_tool(req.tool_name, *req.args, **req.kwargs)
        return {"tool_name": req.tool_name, "result": result, "success": True, "error": None}
    except Exception as e:
        return {"tool_name": req.tool_name, "result": None, "success": False, "error": str(e)}
