"""
Brain module - Core reasoning and search integration.

Combines internet search, vector memory retrieval, and LLM-based reasoning
to answer user queries with full RAG (Retrieval-Augmented Generation).
Supports both synchronous and async streaming responses.
"""

import asyncio
import logging
import re
from backend.core.search import InternetSearch
from backend.core.reasoning import ReasoningEngine
from backend.core.google_dorking import QueryDorker

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
        self.llm = llm_client
        self.memory = memory
        self.vector_memory = vector_memory
        self.search = InternetSearch()
        self.reasoning = ReasoningEngine()
        self.dorker = QueryDorker()
        logger.info("🧠 Brain initialized (vector_memory=%s, dorking=ON)", "ON" if vector_memory else "OFF")

    # ──────────────────────────────────────────────
    # Shared RAG context builder (used by think + think_stream)
    # ──────────────────────────────────────────────

    def _build_rag_context(self, user_query, research_mode=False, fast_mode=False, search_mode="none", language="English"):
        """
        Build the full RAG context: vector memory search, web search, deep scraping, prompt.

        Args:
            search_mode: 'none' | 'web_search' | 'deep_research'

        Returns:
            tuple: (prompt: str, search_results: list, memory_context: list)
        """
        logger.info(f"🤔 Thinking about: '{user_query[:50]}...' (SearchMode: {search_mode}, FastMode: {fast_mode})")

        # 1️⃣ Vector memory search (RAG retrieval) — with relevance filtering
        memory_context = []
        if self.vector_memory:
            raw_results = self.vector_memory.search(user_query, top_k=5)
            # Filter out low-relevance results (cosine distance > 0.8)
            memory_context = [r for r in raw_results if r.get("distance", 1.0) < 0.8]
            logger.debug(f"Retrieved {len(memory_context)} relevant memory results (filtered from {len(raw_results)})")

        # 2️⃣ Internet search — controlled by search_mode
        search_results = []
        deep_research = False

        if search_mode == "none":
            # Pure AI chat — skip web search entirely
            logger.debug("Search mode: none — skipping web search")

        elif search_mode == "web_search":
            # Web search with Google dorking for better accuracy
            dorked_queries = self.dorker.dork(user_query, mode="web_search")
            dorked_query = dorked_queries[0]  # Single optimised query
            logger.info(f"🔍 Web Search (dorked): '{dorked_query}'")
            search_results = self.search.search(dorked_query, max_results=5)
            logger.info(f"🔍 Web Search: {len(search_results)} results")

        elif search_mode == "deep_research":
            # Deep research — multi-query dorking + scrape top pages
            dorked_queries = self.dorker.dork(user_query, mode="deep_research")
            logger.info(f"🕵️ Deep Research (dorked): {dorked_queries}")
            search_results = self.search.search_multiple(
                dorked_queries, max_results_per_query=5
            )
            deep_research = True
            logger.info(f"🕵️ Deep Research: {len(search_results)} unique results (will scrape)")

        else:
            # Legacy fallback — use old heuristics for backward compatibility
            max_results = 5
            if fast_mode:
                max_results = 1
                deep_research = True
            elif "top" in user_query.lower() and any(c.isdigit() for c in user_query):
                match = re.search(r"top\s+(\d+)", user_query.lower())
                if match:
                    max_results = int(match.group(1))
                    deep_research = True
            elif "research" in user_query.lower() or "collect data" in user_query.lower() or research_mode:
                max_results = 10
                deep_research = True

            search_results = self.search.search(user_query, max_results=max_results)
            logger.debug(f"Retrieved {len(search_results)} search results (legacy mode)")

        # Deep Research: Scrape top results
        if deep_research and search_results:
            from backend.tools.browser import scrape_url
            logger.info("🕵️‍♂️ Deep Research activated: Scraping top results...")

            scraped_count = 0
            for result in search_results[:3]:
                try:
                    url = result.get('href', '')
                    if not url:
                        continue
                    content = scrape_url(url)
                    if len(content) > 500:
                        result['body'] += f"\n\n[FULL CONTENT]:\n{content[:2000]}..."
                        scraped_count += 1
                except Exception as e:
                    logger.warning(f"Failed to scrape {url}: {e}")

            logger.info(f"✅ Scraped {scraped_count} pages for deep context")

        # 3️⃣ Get chat history for multi-turn context
        chat_history = self.memory.get_last(n=5)

        # 4️⃣ Build reasoning prompt with all context
        prompt = self.reasoning.build_prompt(
            user_query,
            search_results,
            memory_context=memory_context,
            chat_history=chat_history,
            fast_mode=fast_mode,
            research_mode=research_mode,
            search_mode=search_mode,
            language=language,
        )

        return prompt, search_results, memory_context

    # ──────────────────────────────────────────────
    # Synchronous (full response)
    # ──────────────────────────────────────────────

    def think(self, user_query, research_mode=False, fast_mode=False, search_mode="none", language="English", provider=None, model=None):
        """Process a user query using RAG pipeline. Returns complete response string."""
        try:
            prompt, search_results, memory_context = self._build_rag_context(
                user_query, research_mode, fast_mode, search_mode, language
            )

            # Ask LLM
            active_provider = provider or self.llm.default_provider
            active_model = model  # Will be resolved inside llm.generate
            
            # Resolve model name for metadata
            if not active_model:
                model_map = {
                    "google": "gemini-1.5-flash", "groq": "llama-3.1-8b-instant",
                    "mistral": "mistral-large-latest", "openrouter": "mistralai/mistral-7b-instruct",
                    "openai": "gpt-4o-mini", "nvidia": "moonshotai/kimi-k2.5",
                }
                active_model = model_map.get(active_provider, "unknown")
            
            answer = self.llm.generate(prompt, provider=provider, model=model)
            logger.info(f"✅ Generated answer ({len(answer)} chars)")

            # Save to conversation history with full metadata
            self.memory.remember({
                "user": user_query,
                "jarvis": answer,
                "provider": active_provider,
                "model": active_model,
                "fast_mode": fast_mode,
                "research_mode": research_mode,
                "language": language,
                "response_length": len(str(answer)) if answer else 0,
            })

            return answer

        except Exception as e:
            logger.error(f"❌ Brain error: {e}")
            return f"I encountered an error while processing your query: {str(e)}"

    # ──────────────────────────────────────────────
    # Async streaming (token-by-token)
    # ──────────────────────────────────────────────

    async def think_stream(self, user_query, research_mode=False, fast_mode=False,
                           search_mode="none", language="English", provider=None, model=None):
        """
        Async generator that yields response tokens for streaming.
        Uses the same RAG pipeline as think() but streams the LLM output.
        """
        try:
            prompt, search_results, memory_context = self._build_rag_context(
                user_query, research_mode, fast_mode, search_mode, language
            )

            # Stream from LLM
            full_response = ""
            if hasattr(self.llm, "generate_stream"):
                for token in self.llm.generate_stream(prompt, provider=provider, model=model):
                    full_response += token
                    yield token
            else:
                # Fallback: generate full response, yield in word chunks
                full_response = self.llm.generate(prompt, provider=provider, model=model)
                words = full_response.split(" ")
                chunk_size = 4
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i + chunk_size])
                    if i > 0:
                        chunk = " " + chunk
                    yield chunk
                    await asyncio.sleep(0.05)

            # Save to conversation history after streaming completes
            if full_response:
                active_provider = provider or self.llm.default_provider
                active_model = model
                if not active_model:
                    model_map = {
                        "google": "gemini-1.5-flash", "groq": "llama-3.1-8b-instant",
                        "mistral": "mistral-large-latest", "openrouter": "mistralai/mistral-7b-instruct",
                        "openai": "gpt-4o-mini", "nvidia": "moonshotai/kimi-k2.5",
                    }
                    active_model = model_map.get(active_provider, "unknown")
                
                self.memory.remember({
                    "user": user_query,
                    "jarvis": full_response,
                    "provider": active_provider,
                    "model": active_model,
                    "fast_mode": fast_mode,
                    "research_mode": research_mode,
                    "language": language,
                    "response_length": len(str(full_response)) if full_response else 0,
                })

        except Exception as e:
            logger.error(f"❌ Brain streaming error: {e}")
            yield f"Error: {str(e)}"
