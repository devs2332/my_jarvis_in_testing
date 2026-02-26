"""
Tool permission validation based on subscription plan.
"""

import logging
from server.tools.registry import PLAN_TOOLS

logger = logging.getLogger(__name__)


def validate_tool_permission(
    tool_name: str, plan: str
) -> tuple[bool, str]:
    """
    Check if a tool is allowed for the given plan.
    Returns (allowed, reason).
    """
    allowed_tools = PLAN_TOOLS.get(plan, PLAN_TOOLS["free"])

    if tool_name in allowed_tools:
        return True, "ok"

    return False, (
        f"Tool '{tool_name}' requires a higher plan. "
        f"Your plan ({plan}) allows: {', '.join(allowed_tools)}"
    )


def get_plan_tool_list(plan: str) -> list[str]:
    """Get the list of tools available for a plan."""
    return PLAN_TOOLS.get(plan, PLAN_TOOLS["free"])
