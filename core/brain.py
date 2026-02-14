"""
Brain module - Core reasoning and search integration.

Combines internet search, vector memory retrieval, and LLM-based reasoning
to answer user queries with full RAG (Retrieval-Augmented Generation).
"""

import logging
from core.search import InternetSearch
from core.reasoning import ReasoningEngine

logger = logging.getLogger(__name__)


class Brain:
    """
    The Brain orchestrates search, memory retrieval, and reasoning.

    Attributes:
        llm: LLM client for generating responses
        memory: Key-value memory for facts
        vector_memory: ChromaDB vector store for semantic search
        search: Internet search engine
        reasoning: Reasoning engine for building prompts
    """

    def __init__(self, llm_client, memory, vector_memory=None):
        """
        Initialize the Brain with LLM, memory, and optional vector memory.

        Args:
            llm_client: Initialized LLM client
            memory: Memory instance for key-value facts
            vector_memory: Optional VectorMemory instance for RAG
        """
        self.llm = llm_client
        self.memory = memory
        self.vector_memory = vector_memory
        self.search = InternetSearch()
        self.reasoning = ReasoningEngine()
        logger.info("🧠 Brain initialized (vector_memory=%s)", "ON" if vector_memory else "OFF")

    def think(self, user_query):
        """
        Process a user query using RAG pipeline.

        Steps:
        1. Search vector memory for relevant past context
        2. Search the internet for relevant information
        3. Build a reasoning prompt with all context
        4. Generate response using LLM
        5. Store Q&A in vector memory

        Args:
            user_query (str): The user's question or request

        Returns:
            str: Generated answer from the LLM
        """
        try:
            logger.info(f"🤔 Thinking about: '{user_query[:50]}...'")

            # 1️⃣ Vector memory search (RAG retrieval)
            memory_context = []
            if self.vector_memory:
                memory_context = self.vector_memory.search(user_query, top_k=3)
                logger.debug(f"Retrieved {len(memory_context)} memory results")

            # 2️⃣ Internet search
            search_results = self.search.search(user_query)
            logger.debug(f"Retrieved {len(search_results)} search results")

            # 3️⃣ Build reasoning prompt with all context
            prompt = self.reasoning.build_prompt(
                user_query, search_results, memory_context=memory_context
            )

            # 4️⃣ Ask LLM
            answer = self.llm.generate(prompt)
            logger.info(f"✅ Generated answer ({len(answer)} chars)")

            # 5️⃣ Save to both memory systems
            self.memory.remember({"user": user_query, "jarvis": answer})

            if self.vector_memory:
                self.vector_memory.add_conversation(user_query, answer)

            return answer

        except Exception as e:
            logger.error(f"❌ Brain error: {e}")
            return f"I encountered an error while processing your query: {str(e)}"

