"""
Reasoning engine for building LLM prompts with context.

Creates structured prompts that guide the LLM to reason through problems
using search results, memory context, chat history, and user queries.
"""

import logging

logger = logging.getLogger(__name__)

# Persistent Jarvis system prompt
SYSTEM_PROMPT = """You are Jarvis, an advanced AI assistant with deep reasoning capabilities.
You are helpful, concise, and knowledgeable. You have access to internet search results,
your own memory of past conversations, and various tools.

Key traits:
- Provide accurate, well-reasoned answers
- Cite sources when using search results
- Remember context from past conversations when relevant
- Be direct and avoid unnecessary filler"""


class ReasoningEngine:
    """
    Builds reasoning prompts for LLM-based question answering.

    Combines user queries with search results, vector memory context,
    and chat history to create rich, contextual prompts.
    """

    def __init__(self):
        logger.info("Reasoning engine initialized")

    def build_prompt(self, user_query, search_results, memory_context=None,
                     chat_history=None, fast_mode=False, research_mode=False,
                     language="English"):
        """
        Build a structured reasoning prompt from query, search results, history, and memory.

        Args:
            user_query (str): The user's question or request
            search_results (list): Search result dicts with 'title' and 'body'
            memory_context (list): Optional vector memory results with 'text' key
            chat_history (list): Optional recent conversation turns [{"user": ..., "jarvis": ...}]
            fast_mode (bool): Whether to enforce concise answer
            language (str): Response language ("English" or "Hindi")

        Returns:
            str: Formatted prompt for the LLM
        """
        logger.debug(f"Building reasoning prompt for query: '{user_query[:50]}...'")

        # System prompt
        prompt = SYSTEM_PROMPT + "\n\n"

        # Chat history (last N turns for multi-turn context)
        if chat_history:
            history_lines = []
            for turn in chat_history[-5:]:  # Last 5 turns
                user_msg = turn.get("user", "")
                jarvis_msg = turn.get("jarvis", "")
                if user_msg and jarvis_msg:
                    history_lines.append(f"User: {user_msg[:200]}")
                    history_lines.append(f"Jarvis: {jarvis_msg[:300]}")
            if history_lines:
                prompt += "Recent Conversation:\n"
                prompt += "\n".join(history_lines)
                prompt += "\n\n"

        # Current user query
        prompt += f"User Question:\n{user_query}\n"

        # Vector memory context (past relevant conversations)
        if memory_context:
            mem_entries = []
            for entry in memory_context:
                text = entry.get("text", "")
                if text:
                    mem_entries.append(f"- {text[:300]}")
            if mem_entries:
                prompt += f"\nRelevant Past Knowledge:\n"
                prompt += "\n".join(mem_entries)
                prompt += "\n"

        # Web search results
        web_context = "\n".join(
            f"- {r['title']}: {r['body']}"
            for r in search_results
        )
        if not web_context:
            web_context = "No internet search results available."

        prompt += f"\nInternet Search Results:\n{web_context}\n"

        # ── Formatting instructions (mode-specific) ──
        prompt += "\nFORMATTING RULES (you MUST follow these exactly):\n"

        if fast_mode:
            prompt += """
You are in **FAST MODE**. Follow these rules strictly:
- Give a VERY SHORT answer: 2-4 sentences maximum
- Use bullet points (•) for any list items
- Start directly with the answer — NO introduction, NO preamble
- Do NOT use headers or sections
- Do NOT say "Based on the search results" or similar filler
- If the answer is a single fact, give just that fact in one sentence
- Bold (**word**) only the most critical keyword in your answer

Example format:
**Python** is a high-level programming language.
• Created by Guido van Rossum in 1991
• Used for web dev, AI/ML, automation
"""
        elif research_mode:
            prompt += """
You are in **DEEP RESEARCH MODE**. Follow these rules strictly:
- Structure your answer as a well-organized research report
- Start with a one-line **bold summary** of the answer
- Use markdown `## Section Headers` to organize major topics
- Use `###` for sub-sections when needed
- Use bullet points (- item) and numbered lists (1. item) for details
- Bold (**word**) key terms, names, and important concepts
- Include specific data points, numbers, dates, and statistics when available
- If comparing items, use a markdown table with | Column | Column |
- End with a `## Summary` or `## Key Takeaways` section with 3-5 bullet points
- Cite sources inline like: (Source: website name)
- Aim for a comprehensive, detailed answer — at least 300-500 words

Example structure:
**One-line summary of the topic.**

## Overview
Brief introduction...

## Key Findings
- **Point 1**: Detail...
- **Point 2**: Detail...

## Detailed Analysis
...

## Summary
- Takeaway 1
- Takeaway 2
"""
        else:
            prompt += """
You are in **NORMAL MODE**. Follow these rules:
- Give a clear, well-structured answer
- Use **bold** for key terms and important concepts
- Use bullet points for lists of 3+ items
- Use short paragraphs (2-3 sentences each)
- Use `## Headers` only if the answer has multiple distinct topics
- Be conversational but informative
- Aim for 100-200 words unless the topic needs more
- Do NOT start with "Based on the search results" or similar filler
- Start directly with the answer
"""

        if language and language.lower() == "hindi":
            prompt += "\n- ANSWER IN PURE HINDI (Devanagari script).\n"
            prompt += "- Do not use mixed Hinglish.\n"
            prompt += "- Use technical terms in English if needed, but explain in Hindi.\n"

        prompt += "\nANSWER:\n"

        logger.debug("Reasoning prompt built successfully")
        return prompt

    def build_messages(self, user_query, search_results, memory_context=None,
                       chat_history=None, fast_mode=False, language="English"):
        """
        Build a multi-turn message array for chat-based LLM APIs.

        Returns:
            list[dict]: Messages in OpenAI chat format [{"role": "...", "content": "..."}]
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add chat history as alternating user/assistant messages
        if chat_history:
            for turn in chat_history[-5:]:
                user_msg = turn.get("user", "")
                jarvis_msg = turn.get("jarvis", "")
                if user_msg:
                    messages.append({"role": "user", "content": user_msg[:500]})
                if jarvis_msg:
                    messages.append({"role": "assistant", "content": jarvis_msg[:500]})

        # Build context-enriched user message
        context_parts = []

        if memory_context:
            mem_text = "\n".join(f"- {e.get('text', '')[:300]}" for e in memory_context if e.get("text"))
            if mem_text:
                context_parts.append(f"Relevant Past Knowledge:\n{mem_text}")

        web_context = "\n".join(f"- {r['title']}: {r['body']}" for r in search_results)
        if web_context:
            context_parts.append(f"Search Results:\n{web_context}")

        user_content = user_query
        if context_parts:
            user_content += "\n\n[Context]\n" + "\n\n".join(context_parts)

        if fast_mode:
            user_content += "\n\n(Respond concisely — key facts only)"
        if language and language.lower() == "hindi":
            user_content += "\n\n(Respond in pure Hindi / Devanagari)"

        messages.append({"role": "user", "content": user_content})

        return messages
