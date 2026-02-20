# jarvis_ai/server/app.py
"""
FastAPI application — Jarvis AI Backend Server.

Provides REST + WebSocket API for the React frontend.
Uses lifespan context manager for proper startup/shutdown.
"""

import sys
import os
from contextlib import asynccontextmanager

# Add project root to path so core/ imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize core systems on startup, cleanup on shutdown."""
    from core.agent import Agent
    from core.vector_memory import VectorMemory
    from core.memory import Memory
    from voice.voice_manager import VoiceManager

    # Shared state — accessible via app.state in routes
    app.state.vector_memory = VectorMemory()
    app.state.memory = Memory()
    app.state.agent = Agent(vector_memory=app.state.vector_memory)
    app.state.voice_manager = VoiceManager()

    import logging
    logging.getLogger(__name__).info("🚀 Jarvis AI backend started")

    yield  # App is running

    # Shutdown cleanup
    if app.state.voice_manager:
        app.state.voice_manager.stop()
    logging.getLogger(__name__).info("👋 Jarvis AI backend shutting down")


app = FastAPI(
    title="Jarvis AI",
    description="Advanced AI Assistant API",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
