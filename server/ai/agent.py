"""
LangChain-based AI Agent with OpenAI function calling and streaming.
"""

import logging
from typing import AsyncGenerator, Optional

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from server.app.config import get_settings
from server.ai.prompt_guard import sanitize_input
from server.ai.memory import get_user_memory
from server.ai.token_tracker import calculate_cost

logger = logging.getLogger(__name__)
settings = get_settings()

SYSTEM_PROMPT = """You are Jarvis, an enterprise-grade AI assistant.
You are helpful, accurate, and concise. You have access to various tools
to help users accomplish their tasks. Always think step by step.

Guidelines:
- Be direct and helpful
- Use tools when they would provide better answers
- Cite sources when providing factual information
- Respect user privacy and data boundaries
- Never execute potentially harmful operations without confirmation
"""


def _create_llm(model: str, streaming: bool = False) -> ChatOpenAI:
    """Create an OpenAI LLM instance."""
    return ChatOpenAI(
        model=model,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.7,
        streaming=streaming,
        max_tokens=4096,
    )


def _create_agent(model: str, tools: list = None):
    """Create a LangChain agent with OpenAI function calling."""
    llm = _create_llm(model)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    if tools:
        agent = create_openai_functions_agent(llm, tools, prompt)
        return AgentExecutor(
            agent=agent, tools=tools, verbose=False,
            max_iterations=5, handle_parsing_errors=True,
        )
    else:
        return llm, prompt


async def run_agent(
    message: str,
    model: str = "gpt-4o-mini",
    user_id: str = None,
    tools: list = None,
) -> dict:
    """
    Run the AI agent and return a complete response.
    Returns dict with content, tokens, and cost.
    """
    # Sanitize input
    clean_message = sanitize_input(message)

    # Get conversation history
    history = await get_user_memory(user_id) if user_id else []

    if tools:
        executor = _create_agent(model, tools)
        result = await executor.ainvoke({
            "input": clean_message,
            "chat_history": history,
        })
        content = result.get("output", "")
    else:
        llm = _create_llm(model)
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages.extend(history)
        messages.append(HumanMessage(content=clean_message))

        result = await llm.ainvoke(messages)
        content = result.content

    # Calculate token usage
    usage = result.response_metadata.get("token_usage", {}) if hasattr(result, "response_metadata") else {}
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = prompt_tokens + completion_tokens
    cost = calculate_cost(model, prompt_tokens, completion_tokens)

    return {
        "content": content,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost,
        "model": model,
    }


async def stream_agent(
    message: str,
    model: str = "gpt-4o-mini",
    user_id: str = None,
) -> AsyncGenerator[dict, None]:
    """
    Stream AI agent response token by token.
    Yields dicts with type='token' and type='usage'.
    """
    clean_message = sanitize_input(message)
    history = await get_user_memory(user_id) if user_id else []

    llm = _create_llm(model, streaming=True)

    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(history)
    messages.append(HumanMessage(content=clean_message))

    total_content = ""
    async for chunk in llm.astream(messages):
        if chunk.content:
            total_content += chunk.content
            yield {"type": "token", "content": chunk.content}

    # Final usage info
    prompt_tokens = len(clean_message.split()) * 2  # rough estimate for streaming
    completion_tokens = len(total_content.split()) * 2
    cost = calculate_cost(model, prompt_tokens, completion_tokens)

    yield {
        "type": "usage",
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost_usd": cost,
    }
