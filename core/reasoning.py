"""
Reasoning engine for building LLM prompts with context.

Creates structured prompts that guide the LLM to reason through problems
using search results, memory context, chat history, and user queries.
"""

import logging
import random

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
                     search_mode="none", language="English"):
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
        else:
            web_context += (
                "\n\n(Note: These results were gathered using targeted search operators "
                "for higher accuracy. Prioritise information from authoritative and "
                "official sources like documentation sites, research papers, and "
                "well-known publications.)"
            )

        prompt += f"\nInternet Search Results:\n{web_context}\n"

        # ── Formatting instructions (mode-specific) ──
        prompt += "\nFORMATTING RULES (you MUST follow these exactly):\n"

        if search_mode == "deep_research" or research_mode:
            deep_target = random.randint(200, 300)
            prompt += f"""
You are in **DEEP RESEARCH MODE**. Follow these rules strictly:
- You MUST write a DETAILED and COMPREHENSIVE answer.
- Your answer MUST be exactly **{deep_target} lines** long. This is MANDATORY.
- Structure your answer as a well-organized research report.
- Start with a one-line **bold summary** of the answer.
- Use markdown `## Section Headers` to organize major topics.
- Use `### Sub-sections` to break down topics further.
- Use bullet points (- item) and numbered lists (1. item) extensively.
- Bold (**word**) key terms, names, and important concepts.
- Include ALL specific data points, numbers, dates, statistics, and facts you can find.
- If comparing items, use markdown tables with | Column | Column |.
- Provide multiple perspectives, pros/cons, and detailed analysis.
- Include examples, use cases, and real-world applications.
- Add a `## Detailed Analysis` section with in-depth exploration.
- Add a `## Comparison` section with tables if applicable.
- Add a `## Practical Guide` or `## How-To` section if relevant.
- End with a `## Summary` or `## Key Takeaways` section with 5-10 bullet points.
- Cite sources inline like: (Source: website name).
- DO NOT be brief. DO NOT summarize. Be as detailed and exhaustive as possible.
- If you run out of search context, use your own knowledge to fill in details.
- Remember: AIM FOR {deep_target} lines. This is a comprehensive research report.

Example structure:
**One-line summary of the topic.**

## Overview
Detailed introduction covering background, history, and context...

## Key Findings
### Finding 1
- **Point 1**: Extensive detail with data and examples...
- **Point 2**: More detail...

### Finding 2
...

## Detailed Analysis
In-depth exploration with multiple paragraphs...

## Comparison Table
| Feature | Option A | Option B |
|---------|----------|----------|
| ...     | ...      | ...      |

## Practical Applications
...

## Summary
- Takeaway 1
- Takeaway 2
- Takeaway 3
- Takeaway 4
- Takeaway 5
"""
        elif search_mode == "web_search":
            web_target = random.randint(100, 150)
            prompt += f"""
You are in **WEB SEARCH MODE**. Follow these rules strictly:
- You MUST write a MODERATELY DETAILED answer with good depth.
- Your answer MUST be exactly **{web_target} lines** long. This is MANDATORY.
- Structure your answer clearly with markdown formatting.
- Start with a one-line **bold summary** of the answer.
- Use markdown `## Section Headers` to organize into 3-5 sections.
- Use `###` for sub-sections when needed.
- Use bullet points (- item) and numbered lists (1. item) for details.
- Bold (**word**) key terms, names, and important concepts.
- Include specific data points, numbers, dates, and statistics from search results.
- If comparing items, use a markdown table with | Column | Column |.
- End with a `## Summary` section with 3-5 key takeaways.
- Cite sources inline like: (Source: website name).
- Be thorough — cover all major aspects of the topic.
- Remember: AIM FOR {web_target} lines. Give a well-rounded, informative answer.

Example structure:
**One-line summary of the topic.**

## Overview
Introduction with key context...

## Key Points
- **Point 1**: Detail with data...
- **Point 2**: More detail...

## Analysis
Deeper exploration of the topic...

## Summary
- Takeaway 1
- Takeaway 2
- Takeaway 3
"""
        else:
            default_target = random.randint(6, 60)
            prompt += f"""
You are in **DEFAULT AI CHAT MODE** (no search). Follow these rules strictly:
- Write a clear, helpful answer with basic detail.
- Your answer should be exactly **{default_target} lines** long.
- For simple factual questions, a short 6-15 line answer is fine.
- For explanations or how-to questions, write 30-50 lines.
- For complex topics, write up to 60 lines.
- Start directly with the answer — NO filler phrases like "Based on my knowledge".
- Use markdown formatting when helpful (bold, bullets, headers for longer answers).
- Bold (**word**) key terms and important concepts.
- Use bullet points for lists and key points.
- Use code blocks with language tags for any code examples.
- Be direct, concise, and useful.
- Match your answer length to the complexity of the question.

Example format for a simple question:
**Python** is a high-level programming language created by Guido van Rossum.
- Used for web development, AI/ML, automation, and data science
- Known for its readable syntax and large ecosystem

Example format for a complex question:
## Overview
Explanation of the topic...

## Key Points
- **Point 1**: Detail...
- **Point 2**: Detail...

## Summary
- Key takeaway
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
