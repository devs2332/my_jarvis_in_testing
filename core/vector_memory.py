# jarvis_ai/core/vector_memory.py
"""
Vector Memory using ChromaDB for semantic search and RAG.

Stores conversation history and knowledge as vector embeddings,
enabling semantic similarity search for context-aware responses.
"""

import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorMemory:
    """
    ChromaDB-backed vector memory for semantic search.

    Stores text documents with embeddings for similarity retrieval.
    Uses sentence-transformers for local embedding generation.
    """

    def __init__(self, persist_dir=None, collection_name="jarvis_memory"):
        """
        Initialize vector memory.

        Args:
            persist_dir: Directory to persist ChromaDB data (default: ./data/vector_db)
            collection_name: Name of the ChromaDB collection
        """
        import chromadb
        from chromadb.config import Settings

        if persist_dir is None:
            persist_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data", "vector_db"
            )

        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_dir)

        # Use ChromaDB's default embedding function (all-MiniLM-L6-v2)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(
            f"🧠 Vector Memory initialized — "
            f"{self.collection.count()} documents in '{collection_name}'"
        )

    def add(self, text, metadata=None, doc_id=None):
        """
        Add a document to vector memory.

        Args:
            text (str): Document text to embed and store
            metadata (dict): Optional metadata (type, timestamp, etc.)
            doc_id (str): Optional unique ID (auto-generated if None)

        Returns:
            str: The document ID
        """
        if doc_id is None:
            doc_id = f"doc_{int(time.time() * 1000)}"

        if metadata is None:
            metadata = {}

        metadata["timestamp"] = time.time()
        metadata["length"] = len(text)

        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )

        logger.debug(f"Added document '{doc_id}' ({len(text)} chars)")
        return doc_id

    def add_conversation(self, user_msg, assistant_msg):
        """
        Store a conversation exchange as a single document.

        Args:
            user_msg (str): User's message
            assistant_msg (str): Assistant's response

        Returns:
            str: The document ID
        """
        combined = f"User: {user_msg}\nAssistant: {assistant_msg}"
        return self.add(
            text=combined,
            metadata={
                "type": "conversation",
                "user_message": user_msg[:200],  # truncate for metadata
                "assistant_preview": assistant_msg[:200],
            }
        )

    def search(self, query, top_k=5):
        """
        Semantic similarity search.

        Args:
            query (str): Search query
            top_k (int): Number of results to return

        Returns:
            list[dict]: Results with keys: id, text, metadata, distance
        """
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count())
        )

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            })

        logger.debug(f"Search '{query[:40]}...' returned {len(output)} results")
        return output

    def get_recent(self, n=10):
        """
        Get the most recent N documents (by timestamp).

        Args:
            n (int): Number of recent documents

        Returns:
            list[dict]: Documents sorted by timestamp descending
        """
        if self.collection.count() == 0:
            return []

        all_docs = self.collection.get(
            limit=min(n * 2, self.collection.count()),
            include=["documents", "metadatas"]
        )

        items = []
        for i in range(len(all_docs["ids"])):
            items.append({
                "id": all_docs["ids"][i],
                "text": all_docs["documents"][i],
                "metadata": all_docs["metadatas"][i] if all_docs["metadatas"] else {},
            })

        # Sort by timestamp descending
        items.sort(key=lambda x: x["metadata"].get("timestamp", 0), reverse=True)
        return items[:n]

    def get_stats(self):
        """
        Get vector memory statistics.

        Returns:
            dict: Stats including count, collection name
        """
        return {
            "total_documents": self.collection.count(),
            "collection_name": self.collection.name,
        }

    def delete(self, doc_id):
        """Delete a document by ID."""
        self.collection.delete(ids=[doc_id])
        logger.debug(f"Deleted document '{doc_id}'")

    def clear(self):
        """Clear all documents from the collection."""
        if self.collection.count() > 0:
            all_ids = self.collection.get()["ids"]
            self.collection.delete(ids=all_ids)
        logger.info("🗑️ Vector memory cleared")
