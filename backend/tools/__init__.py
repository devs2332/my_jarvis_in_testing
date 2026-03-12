"""
Tools module for Jarvis AI Assistant.

This package contains various tool functions for:
- Browser operations: web browsing and search
- File operations: reading, writing, and listing files
- System operations: executing commands and system control
"""

from backend.tools.browser import open_url, search_google, get_search_results
from backend.tools.files import read_file, write_file, list_dir
from backend.tools.system import (
    execute_command,
    get_system_info,
    shutdown,
    restart
)

__all__ = [
    # Browser tools
    'open_url',
    'search_google',
    'get_search_results',
    
    # File tools
    'read_file',
    'write_file',
    'list_dir',
    
    # System tools
    'execute_command',
    'get_system_info',
    'shutdown',
    'restart',
]
