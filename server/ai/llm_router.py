"""
Cost-aware LLM router — selects model based on subscription plan.
Includes fallback logic for reliability.
"""

import logging
from server.app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Plan → model mapping
PLAN_MODEL_MAP = {
    "free": settings.MODEL_FREE,
    "pro": settings.MODEL_PRO,
    "enterprise": settings.MODEL_ENTERPRISE,
}

# Model → cost per 1K tokens (input, output)
MODEL_COSTS = {
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
}

# Fallback chain
FALLBACK_CHAIN = {
    "gpt-4o": ["gpt-4-turbo", "gpt-4o-mini"],
    "gpt-4-turbo": ["gpt-4o", "gpt-4o-mini"],
    "gpt-4o-mini": [],  # No fallback for cheapest model
}


def route_model(plan: str, override: str = None) -> str:
    """
    Select the appropriate model based on the user's plan.
    Allows model override for pro/enterprise users.
    """
    if override and plan in ("pro", "enterprise"):
        if override in MODEL_COSTS:
            return override
        logger.warning(f"Invalid model override '{override}', using plan default")

    return PLAN_MODEL_MAP.get(plan, settings.MODEL_FALLBACK)


def get_fallback_model(model: str) -> str:
    """Get the next fallback model if the primary fails."""
    chain = FALLBACK_CHAIN.get(model, [])
    if chain:
        return chain[0]
    return settings.MODEL_FALLBACK


def get_model_cost(model: str) -> dict:
    """Get the cost per 1K tokens for a model."""
    return MODEL_COSTS.get(model, {"input": 0.0, "output": 0.0})


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate the cost for a given number of tokens."""
    costs = get_model_cost(model)
    return (
        (input_tokens / 1000) * costs["input"]
        + (output_tokens / 1000) * costs["output"]
    )
