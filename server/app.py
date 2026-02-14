# jarvis_ai/server/app.py
"""
FastAPI application — Jarvis AI Backend Server.

Provides REST + WebSocket API for the React frontend.
"""

import sys
import os

# Add project root to path so core/ imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routes import router, startup_handler, shutdown_handler

app = FastAPI(
    title="Jarvis AI",
    description="Advanced AI Assistant API",
    version="2.0.0",
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

@app.on_event("startup")
async def on_startup():
    await startup_handler()

@app.on_event("shutdown")
async def on_shutdown():
    await shutdown_handler()
