"""
Unified tool registry and management.

Central registry for all Jarvis tools with metadata and discovery.
"""

import logging
from tools import browser, files, system

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for all available tools.
    
    Provides tool discovery, metadata, and unified access.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self.tools = {}
        self._register_default_tools()
        logger.info(f"🛠️ Tool Registry initialized with {len(self.tools)} tools")
    
    def _register_default_tools(self):
        """Register all default tools."""
        # Browser tools
        self.register_tool(
            "browser.open_url",
            browser.open_url,
            "Open a URL in the browser",
            {"url": "URL to open"}
        )
        self.register_tool(
            "browser.search_google",
            browser.search_google,
            "Search Google for a query",
            {"query": "Search query"}
        )
        
        # File tools
        self.register_tool(
            "files.read_file",
            files.read_file,
            "Read contents of a file",
            {"path": "File path"}
        )
        self.register_tool(
            "files.write_file",
            files.write_file,
            "Write content to a file",
            {"path": "File path", "content": "Content to write"}
        )
        self.register_tool(
            "files.list_dir",
            files.list_dir,
            "List files in a directory",
            {"path": "Directory path"}
        )
        
        # System tools
        self.register_tool(
            "system.execute_command",
            system.execute_command,
            "Execute a system command",
            {"command": "Command to execute"}
        )
        self.register_tool(
            "system.get_system_info",
            system.get_system_info,
            "Get system information",
            {}
        )
        
        # Vision tools (if available)
        try:
            from vision import screen_reader, image_analysis
            
            self.register_tool(
                "vision.read_screen",
                lambda: screen_reader.ScreenReader().read_screen(),
                "Read text from the screen using OCR",
                {}
            )
            self.register_tool(
                "vision.analyze_image",
                lambda path: image_analysis.ImageAnalyzer().analyze_image(path),
                "Analyze an image file",
                {"path": "Image file path"}
            )
            logger.info("✅ Vision tools registered")
        except ImportError:
            logger.warning("⚠️ Vision tools not available (missing dependencies)")
    
    def register_tool(self, name, function, description, parameters):
        """
        Register a new tool.
        
        Args:
            name (str): Tool name (e.g., "browser.open_url")
            function (callable): Tool function
            description (str): Tool description
            parameters (dict): Parameter descriptions
        """
        self.tools[name] = {
            "function": function,
            "description": description,
            "parameters": parameters
        }
        logger.debug(f"Registered tool: {name}")
    
    def get_tool(self, name):
        """
        Get a tool by name.
        
        Args:
            name (str): Tool name
            
        Returns:
            dict: Tool metadata or None
        """
        return self.tools.get(name)
    
    def list_tools(self):
        """
        Get list of all registered tools.
        
        Returns:
            list: List of tool names
        """
        return list(self.tools.keys())
    
    def execute_tool(self, name, **kwargs):
        """
        Execute a tool by name.
        
        Args:
            name (str): Tool name
            **kwargs: Tool parameters
            
        Returns:
            Any: Tool execution result
        """
        tool = self.get_tool(name)
        if tool is None:
            logger.error(f"❌ Tool not found: {name}")
            return f"Error: Tool '{name}' not found"
        
        try:
            logger.info(f"🔧 Executing tool: {name}")
            result = tool["function"](**kwargs)
            logger.info(f"✅ Tool executed successfully: {name}")
            return result
        except Exception as e:
            logger.error(f"❌ Tool execution error ({name}): {e}")
            return f"Error executing {name}: {str(e)}"
