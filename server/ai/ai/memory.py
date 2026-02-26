"""
Per-user conversation memory using Chroma vector store.
"""

import logging
from typing import Optional

from langchain_core.messages import HumanMessage, AIMessage

from server.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# In-memory conversation store (per-user, recent messages)
# For production, use Chroma or another vector DB
_conversation_store: dict[str, list] = {}

MAX_HISTORY_LENGTH = 20


async def get_user_memory(user_id: str) -> list:
    """
    Retrieve conversation history for a user.
    Returns a list of LangChain message objects.
    """
    history = _conversation_store.get(user_id, [])
    return history[-MAX_HISTORY_LENGTH:]


async def add_to_memory(
    user_id: str, role: str, content: str
) -> None:
    """Add a message to the user's conversation memory."""
    if user_id not in _conversation_store:
        _conversation_store[user_id] = []

    if role == "user":
        _conversation_store[user_id].append(HumanMessage(content=content))
    elif role == "assistant":
        _conversation_store[user_id].append(AIMessage(content=content))

    # Trim to max length
    if len(_conversation_store[user_id]) > MAX_HISTORY_LENGTH * 2:
        _conversation_store[user_id] = _conversation_store[user_id][-MAX_HISTORY_LENGTH:]


async def clear_user_memory(user_id: str) -> None:
    """Clear a user's conversation memory."""
    _conversation_store.pop(user_id, None)


def get_chroma_memory(user_id: str):
    """
    Get a Chroma-backed vector memory for long-term storage.
    Falls back to in-memory if Chroma is unavailable.
    """
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        client = chromadb.Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIR,
        ))

        collection = client.get_or_create_collection(
            name=f"user_{user_id}",
            metadata={"hnsw:space": "cosine"},
        )

        return collection
    except ImportError:
        logger.warning("ChromaDB not installed, using in-memory only")
        return None
    except Exception as e:
        logger.error(f"Chroma initialization error: {e}")
        return None
