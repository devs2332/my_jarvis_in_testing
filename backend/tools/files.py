"""
File operation tools.

Provides functions for reading, writing, and listing files.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Safety: Maximum file size to read/write (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def read_file(path: str):
    """
    Reads a text file.
    
    Args:
        path (str): Path to the file
        
    Returns:
        str: File contents or error message
        
    Example:
        >>> content = read_file("config.txt")
    """
    try:
        if not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return "File not found."
        
        file_size = os.path.getsize(path)
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {path} ({file_size} bytes)")
            return f"File too large (max {MAX_FILE_SIZE} bytes)."
        
        logger.info(f"📖 Reading file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        logger.info(f"✅ Read {len(content)} characters from {path}")
        return content
        
    except Exception as e:
        logger.error(f"❌ Error reading file {path}: {e}")
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str):
    """
    Writes content to a file.
    
    Args:
        path (str): Path to the file
        content (str): Content to write
        
    Returns:
        str: Success message or error
        
    Example:
        >>> write_file("output.txt", "Hello World")
        'Written to output.txt'
    """
    try:
        if len(content) > MAX_FILE_SIZE:
            logger.warning(f"Content too large for {path}")
            return f"Content too large (max {MAX_FILE_SIZE} bytes)."
        
        logger.info(f"✍️ Writing to file: {path}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        logger.info(f"✅ Written {len(content)} characters to {path}")
        return f"Written to {path}"
        
    except Exception as e:
        logger.error(f"❌ Error writing file {path}: {e}")
        return f"Error writing file: {str(e)}"


def list_dir(path: str = "."):
    """
    Lists files in a directory.
    
    Args:
        path (str): Directory path (default: current directory)
        
    Returns:
        list or str: List of filenames or error message
        
    Example:
        >>> files = list_dir(".")
        >>> print(files)
        ['file1.txt', 'file2.py', ...]
    """
    try:
        if not os.path.exists(path):
            logger.warning(f"Directory not found: {path}")
            return "Directory not found."
        
        if not os.path.isdir(path):
            logger.warning(f"Not a directory: {path}")
            return "Not a directory."
        
        logger.info(f"📂 Listing directory: {path}")
        files = os.listdir(path)
        logger.info(f"✅ Found {len(files)} items in {path}")
        return files
        
    except Exception as e:
        logger.error(f"❌ Error listing directory {path}: {e}")
        return f"Error listing directory: {str(e)}"
