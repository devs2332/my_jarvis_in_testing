"""
Token usage tracking and cost calculation.
"""

import logging

logger = logging.getLogger(__name__)

# Model pricing per 1K tokens (USD)
MODEL_PRICING = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}


def calculate_cost(
    model: str, prompt_tokens: int, completion_tokens: int
) -> float:
    """Calculate the cost in USD for a given number of tokens."""
    pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})
    cost = (
        (prompt_tokens / 1000) * pricing["input"]
        + (completion_tokens / 1000) * pricing["output"]
    )
    return round(cost, 6)


def estimate_tokens(text: str) -> int:
    """Rough estimate of token count from text (~4 chars per token)."""
    return max(1, len(text) // 4)


def format_cost(cost_usd: float) -> str:
    """Format a cost value for display."""
    if cost_usd < 0.01:
        return f"${cost_usd:.4f}"
    return f"${cost_usd:.2f}"
