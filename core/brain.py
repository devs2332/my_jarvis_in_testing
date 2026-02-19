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

    def think(self, user_query, research_mode=False, fast_mode=False, language="English", provider=None, model=None):
        """
        Process a user query using RAG pipeline.
        """
        try:
            logger.info(f"🤔 Thinking about: '{user_query[:50]}...' (FastMode: {fast_mode})")

            # 1️⃣ Vector memory search (RAG retrieval)
            memory_context = []
            if self.vector_memory:
                memory_context = self.vector_memory.search(user_query, top_k=3)
                logger.debug(f"Retrieved {len(memory_context)} memory results")

            # 2️⃣ Internet search
            # Check for "deep research" intent (e.g. "top 10", "detailed report")
            max_results = 5
            deep_research = False
            
            if fast_mode:
                max_results = 1
                deep_research = True  # FastMode always scrapes the top result
            
            elif "top" in user_query.lower() and any(c.isdigit() for c in user_query):
                import re
                match = re.search(r"top\s+(\d+)", user_query.lower())
                if match:
                    max_results = int(match.group(1))
                    deep_research = True
            
            elif "research" in user_query.lower() or "collect data" in user_query.lower() or research_mode:
                max_results = 10
                deep_research = True

            search_results = self.search.search(user_query, max_results=max_results)
            logger.debug(f"Retrieved {len(search_results)} search results")
            
            # Deep Research: Scrape top results if needed
            if deep_research and search_results:
                from tools.browser import scrape_url
                logger.info("🕵️‍♂️ Deep Research activated: Scraping top results...")
                
                scraped_count = 0
                for result in search_results[:3]: # Scrape top 3 to avoid taking too long
                    try:
                        url = result.get('href', '')
                        if not url: continue
                        
                        content = scrape_url(url)
                        if len(content) > 500:
                            result['body'] += f"\n\n[FULL CONTENT]:\n{content[:2000]}..." # Append first 2k chars
                            scraped_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to scrape {url}: {e}")
                
                logger.info(f"✅ Scraped {scraped_count} pages for deep context")

            # 3️⃣ Build reasoning prompt with all context
            prompt = self.reasoning.build_prompt(
                user_query, search_results, memory_context=memory_context, fast_mode=fast_mode, language=language
            )

            # Removed strict formatting rules to allow natural conversation

            # 4️⃣ Ask LLM
            answer = self.llm.generate(prompt, provider=provider, model=model)
            logger.info(f"✅ Generated answer ({len(answer)} chars)")

            # 5️⃣ Save to both memory systems
            self.memory.remember({"user": user_query, "jarvis": answer})

            if self.vector_memory:
                self.vector_memory.add_conversation(user_query, answer)

            return answer

        except Exception as e:
            logger.error(f"❌ Brain error: {e}")
            return f"I encountered an error while processing your query: {str(e)}"

