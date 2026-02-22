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

    def run(self, user_input, research_mode=False, fast_mode=False, search_mode="none", language="English", provider=None, model=None):
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

        # 4️⃣ Parse mode prefixes
        user_input, fast_mode, language = self._parse_prefixes(user_input, fast_mode, language)

        # 5️⃣ Try LLM with tool-calling (single-turn: call → execute → respond)
        try:
            from core.tool_schemas import get_tool_schemas
            tool_schemas = get_tool_schemas()
            
            llm_result = self.llm.generate_with_tools(
                user_input, tools=tool_schemas, provider=provider, model=model
            )
            
            if llm_result.get("type") == "tool_call":
                tool_name = llm_result["tool_name"]
                tool_args = llm_result.get("tool_args", {})
                
                logger.info(f"🔧 LLM requested tool: {tool_name} with args: {tool_args}")
                self.state.set("EXECUTING")
                
                # Execute the tool
                if isinstance(tool_args, dict):
                    tool_result = self.tool_registry.execute_tool(tool_name, **tool_args)
                else:
                    tool_result = self.tool_registry.execute_tool(tool_name, *tool_args)
                
                # Feed tool result back to LLM for final response
                followup = f"Tool '{tool_name}' returned: {tool_result}\n\nBased on this result, provide a helpful response to the user's original request: {user_input}"
                response = self.brain.think(
                    followup, fast_mode=fast_mode, language=language,
                    provider=provider, model=model,
                )
                self.state.set("SPEAKING")
                return response
        except Exception as e:
            logger.debug(f"Tool-calling skipped: {e}")

        # 6️⃣ Standard LLM with RAG context (fallback if no tool call)
        response = self.brain.think(
            user_input, research_mode=research_mode, fast_mode=fast_mode,
            search_mode=search_mode, language=language, provider=provider, model=model,
        )
        self.state.set("SPEAKING")
        return response

    async def run_stream(self, user_input, research_mode=False, fast_mode=False,
                         search_mode="none", language="English", provider=None, model=None):
        """
        Async generator that yields response tokens for WebSocket streaming.
        Delegates to brain.think_stream() for clean RAG + streaming.
        """
        self.state.set("THINKING")

        # Check for quick routes first
        result, route = self.router.route(user_input)
        if route in ("memory", "tool"):
            self.state.set("SPEAKING")
            yield result
            return

        # Parse mode prefixes
        user_input, fast_mode, language = self._parse_prefixes(user_input, fast_mode, language)

        # Stream from Brain (single source of RAG logic)
        async for token in self.brain.think_stream(
            user_input, research_mode=research_mode, fast_mode=fast_mode,
            search_mode=search_mode, language=language, provider=provider, model=model,
        ):
            yield token

        self.state.set("SPEAKING")

    @staticmethod
    def _parse_prefixes(user_input, fast_mode, language):
        """Extract FastMode: and HindiMode: prefixes from user input."""
        if user_input.lower().startswith("fastmode:"):
            fast_mode = True
            user_input = user_input[9:].strip()

        if user_input.lower().startswith("hindimode:") or user_input.lower().startswith("hindi:"):
            language = "Hindi"
            if user_input.lower().startswith("hindimode:"):
                user_input = user_input[10:].strip()
            else:
                user_input = user_input[6:].strip()

        return user_input, fast_mode, language
