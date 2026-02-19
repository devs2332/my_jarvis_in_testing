"""
Reasoning engine for building LLM prompts with context.

Creates structured prompts that guide the LLM to reason through problems
using search results, memory context, and user queries.
"""

import logging

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Builds reasoning prompts for LLM-based question answering.

    Combines user queries with search results and vector memory context
    to create rich, contextual prompts for accurate responses.
    """

    def __init__(self):
        """Initialize the reasoning engine."""
        logger.info("Reasoning engine initialized")

    def build_prompt(self, user_query, search_results, memory_context=None, fast_mode=False, language="English"):
        """
        Build a structured reasoning prompt from query, search results, and memory.

        Args:
            user_query (str): The user's question or request
            search_results (list): Search result dicts with 'title' and 'body'
            memory_context (list): Optional vector memory results with 'text' key
            fast_mode (bool): Whether to enforce concise answer for FastMode

        Returns:
            str: Formatted prompt for the LLM
        """
        logger.debug(f"Building reasoning prompt for query: '{user_query[:50]}...'")

        # Format search results
        web_context = "\n".join(
            f"- {r['title']}: {r['body']}"
            for r in search_results
        )
        if not web_context:
            web_context = "No internet search results available."

        # Format memory context (from vector DB)
        mem_context = ""
        if memory_context:
            mem_entries = []
            for entry in memory_context:
                text = entry.get("text", "")
                if text:
                    mem_entries.append(f"- {text[:300]}")
            if mem_entries:
                mem_context = "\n".join(mem_entries)

        # Build the full prompt
        prompt = f"""You are an advanced reasoning AI assistant named Jarvis.

User Question:
{user_query}
"""

        if mem_context:
            prompt += f"""
Relevant Past Conversations:
{mem_context}
"""

        prompt += f"""
Internet Search Results:
{web_context}

TASK:
- Consider the past conversation context if relevant
- Analyze the search information"""

        if fast_mode:
            prompt += """
- Provide a very CONCISE and direct answer
- Do not use filler words
- Focus on the key facts from the search result"""
        else:
            prompt += """
- Give a clear, concise, and helpful final answer.
- Avoid unnecessary "Analysis" or "Step-by-step" breakdown unless asked."""

        if language and language.lower() == "hindi":
            prompt += """
- ANSWER IN PURE HINDI (Devanagari script).
- Do not use mixed Hinglish.
- Use technical terms in English if needed, but explain in Hindi.
"""
        else:
            prompt += """
- Answer in standard English.
"""

        prompt += """
FINAL ANSWER:
"""

        logger.debug("Reasoning prompt built successfully")
        return prompt

