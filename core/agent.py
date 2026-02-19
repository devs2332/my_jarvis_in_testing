# jarvis_ai/core/agent.py
"""
Agent — Central orchestrator for Jarvis AI.

Routes user input through intent detection, planning, and LLM reasoning.
Supports both synchronous and async streaming responses.
"""

import asyncio
import logging
from core.state import StateManager
from core.memory import Memory
from core.brain import Brain
from core.intent_router import IntentRouter
from core.planner import Planner
from core.llm_client import LLMClient
from core.tools import ToolRegistry

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self, vector_memory=None):
        self.state = StateManager()
        self.memory = Memory()
        self.vector_memory = vector_memory
        self.llm = LLMClient()
        self.brain = Brain(self.llm, self.memory, vector_memory=vector_memory)
        self.router = IntentRouter(self.memory)
        self.planner = Planner(self.state)
        self.tool_registry = ToolRegistry()
        logger.info("🤖 Agent initialized (vector_memory=%s)", "ON" if vector_memory else "OFF")

    def run(self, user_input, research_mode=False, fast_mode=False, language="English", provider=None, model=None):
        """Process user input and return a response string."""
        self.state.set("THINKING")

        # 1️⃣ Route intent
        result, route = self.router.route(user_input)

        # 2️⃣ Memory / Tool handled
        if route in ("memory", "tool"):
            self.state.set("SPEAKING")
            return result

        # 3️⃣ Planner (for complex tasks)
        if "plan" in user_input.lower() or "task" in user_input.lower():
            plan = self.planner.create_plan(user_input)
            if plan:
                self.state.set("EXECUTING")
                results = []
                for step in plan:
                    action = step.get("action")
                    args = step.get("args", [])
                    try:
                        res = self.tool_registry.execute_tool(action, *args)
                        results.append(f"Step {action}: {res}")
                    except Exception as e:
                        results.append(f"Error in {action}: {e}")

                final_response = "Task completed.\n" + "\n".join(results)
                self.state.set("SPEAKING")
                return final_response

        # 4️⃣ LLM with RAG context
        if user_input.lower().startswith("fastmode:"):
            fast_mode = True
            user_input = user_input[9:].strip()  # Strip 'FastMode:'
        
        if user_input.lower().startswith("hindimode:") or user_input.lower().startswith("hindi:"):
            language = "Hindi"
            if user_input.lower().startswith("hindimode:"):
                user_input = user_input[10:].strip()
            else:
                user_input = user_input[6:].strip()

        response = self.brain.think(user_input, research_mode=research_mode, fast_mode=fast_mode, language=language, provider=provider, model=model)
        self.state.set("SPEAKING")
        return response

    async def run_stream(self, user_input, research_mode=False, fast_mode=False, language="English", provider=None, model=None):
        """
        Async generator that yields response tokens for WebSocket streaming.
        Falls back to chunked non-streaming if provider doesn't support streaming.
        """
        self.state.set("THINKING")

        # Check for quick routes first
        result, route = self.router.route(user_input)
        if route in ("memory", "tool"):
            self.state.set("SPEAKING")
            yield result
            return

        # Stream from LLM
        self.state.set("THINKING")
        if hasattr(self.llm, "generate_stream"):
            # Strip prefixes if present in streaming mode
            if user_input.lower().startswith("fastmode:"):
                fast_mode = True
                user_input = user_input[9:].strip()
            
            if user_input.lower().startswith("hindimode:") or user_input.lower().startswith("hindi:"):
                language = "Hindi"
                if user_input.lower().startswith("hindimode:"):
                    user_input = user_input[10:].strip()
                else:
                    user_input = user_input[6:].strip()

            # Build prompt with RAG context
            # Note: For now run_stream duplicates some brain logic, 
            # ideally we should use brain.think_stream() but modifying brain.think() is enough for now.
            # We will use brain.think() for context building logic if we refactor,
            # but here we just need to ensure parameters are respected.
            
            # Since strict equality with brain.think is complex due to streaming, we will patch it here:
            max_results = 5
            deep_research = False
            
            if fast_mode:
                max_results = 1
                deep_research = True
            elif research_mode or "research" in user_input.lower():
                max_results = 10
                deep_research = True
            
            search_results = self.brain.search.search(user_input, max_results=max_results)
            
            # Deep Research / FastMode Scraping
            if deep_research and search_results:
                from tools.browser import scrape_url
                for result in search_results[:3]:
                    try:
                        url = result.get('href', '')
                        if url:
                            content = scrape_url(url)
                            if len(content) > 500:
                                result['body'] += f"\n\n[FULL CONTENT]:\n{content[:2000]}..."
                    except Exception:
                        pass
            
            memory_context = []
            if self.vector_memory:
                memory_context = self.vector_memory.search(user_input, top_k=3)
            
            prompt = self.brain.reasoning.build_prompt(
                user_input, search_results, memory_context=memory_context, fast_mode=fast_mode, language=language
            )
            
            # Apply formatting rules to ALL prompts
            prompt += """
FORMATTING RULES - STRICTLY FOLLOW THESE:
1. **Structure**: Use clear headings (# Phase 1, ## Goal) and subheadings.
2. **Bullet Points**: Use bullet points for lists. Do NOT write comma-separated lists in a paragraph.
3. **Spacing**: Add a blank line between every paragraph or list item.
4. **Bold Text**: Use **bold** for key terms and concepts.
5. **Conciseness**: Keep paragraphs short (max 2-3 sentences).

EXAMPLE FORMAT (for Plans/Roadmaps):
# Phase 1
**Goal**: Technical Foundation
- Point 1
- Point 2
"""

            for token in self.llm.generate_stream(prompt, provider=provider, model=model):
                yield token
        else:
            # Fallback: get full response, yield in chunks
            if user_input.lower().startswith("fastmode:"):
                fast_mode = True
                user_input = user_input[9:].strip()

            if user_input.lower().startswith("hindimode:") or user_input.lower().startswith("hindi:"):
                language = "Hindi"
                if user_input.lower().startswith("hindimode:"):
                    user_input = user_input[10:].strip()
                else:
                    user_input = user_input[6:].strip()

            response = self.brain.think(user_input, research_mode=research_mode, fast_mode=fast_mode, language=language, provider=provider, model=model)
            chunk_size = 4
            words = response.split(" ")
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if i > 0:
                    chunk = " " + chunk
                yield chunk
                await asyncio.sleep(0.05)

        self.state.set("SPEAKING")
