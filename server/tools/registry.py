"""
Tool registry — dynamic tool loading and management.
"""

import logging
from typing import Dict, List, Optional
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# Global tool registry
_tool_registry: Dict[str, BaseTool] = {}

# Plan → allowed tools
PLAN_TOOLS = {
    "free": ["web_search"],
    "pro": ["web_search", "browser_automation", "system_info"],
    "enterprise": ["web_search", "browser_automation", "system_control", "system_info"],
}


def register_tool(tool: BaseTool) -> None:
    """Register a tool in the global registry."""
    _tool_registry[tool.name] = tool
    logger.info(f"Registered tool: {tool.name}")


def get_tool(name: str) -> Optional[BaseTool]:
    """Get a tool by name."""
    return _tool_registry.get(name)


def get_tools_for_plan(plan: str) -> List[BaseTool]:
    """Get all tools available for a subscription plan."""
    allowed_names = PLAN_TOOLS.get(plan, PLAN_TOOLS["free"])
    return [
        tool for name, tool in _tool_registry.items()
        if name in allowed_names
    ]


def list_tools() -> List[dict]:
    """List all registered tools with metadata."""
    return [
        {
            "name": tool.name,
            "description": tool.description,
        }
        for tool in _tool_registry.values()
    ]


def init_default_tools():
    """Register the default tool set."""
    from server.tools.search_tool import WebSearchTool
    from server.tools.browser_tool import BrowserAutomationTool
    from server.tools.system_tool import SystemInfoTool, SystemControlTool

    register_tool(WebSearchTool())
    register_tool(BrowserAutomationTool())
    register_tool(SystemInfoTool())
    register_tool(SystemControlTool())

    logger.info(f"Initialized {len(_tool_registry)} default tools")
