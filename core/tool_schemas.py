# jarvis_ai/core/tool_schemas.py
"""
OpenAI function-calling compatible JSON schemas for all registered tools.
Used by LLMClient.generate_with_tools() for structured tool invocation.
"""

# OpenAI-compatible function definitions
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "browser.open_url",
            "description": "Open a URL in the default web browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to open (e.g. 'google.com')"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser.search_google",
            "description": "Search Google for a query and open results in browser",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browser.scrape_url",
            "description": "Scrape and extract text content from a web page URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to scrape"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "files.read_file",
            "description": "Read the contents of a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "files.write_file",
            "description": "Write content to a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "files.list_dir",
            "description": "List files and folders in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path (default: current dir)", "default": "."}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "system.execute_command",
            "description": "Execute a system shell command (use with caution)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "system.get_system_info",
            "description": "Get basic system information (OS, architecture, time)",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


def get_tool_schemas():
    """Return all tool schemas in OpenAI function-calling format."""
    return TOOL_SCHEMAS


def get_tool_names():
    """Return list of available tool names."""
    return [t["function"]["name"] for t in TOOL_SCHEMAS]


def get_schema_for_tool(tool_name):
    """Get the schema for a specific tool by name."""
    for t in TOOL_SCHEMAS:
        if t["function"]["name"] == tool_name:
            return t
    return None
