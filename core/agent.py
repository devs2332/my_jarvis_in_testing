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

    def run(self, user_input):
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
        response = self.brain.think(user_input)
        self.state.set("SPEAKING")
        return response

    async def run_stream(self, user_input):
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
            # Build prompt with RAG context
            search_results = self.brain.search.search(user_input)
            memory_context = []
            if self.vector_memory:
                memory_context = self.vector_memory.search(user_input, top_k=3)
            prompt = self.brain.reasoning.build_prompt(
                user_input, search_results, memory_context=memory_context
            )
            for token in self.llm.generate_stream(prompt):
                yield token
        else:
            # Fallback: get full response, yield in chunks
            response = self.brain.think(user_input)
            chunk_size = 4
            words = response.split(" ")
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                if i > 0:
                    chunk = " " + chunk
                yield chunk
                await asyncio.sleep(0.05)

        self.state.set("SPEAKING")
