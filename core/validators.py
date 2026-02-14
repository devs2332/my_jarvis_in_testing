"""
Input and output validators for Jarvis AI.

Provides validation and sanitization for user inputs and system outputs.
"""

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validates user inputs for safety and correctness.
    """
    
    @staticmethod
    def is_safe_path(path_str):
        """
        Check if a file path is safe to use.
        
        Args:
            path_str (str): Path to validate
            
        Returns:
            bool: True if path is safe
        """
        try:
            # Resolve to absolute path
            path = Path(path_str).resolve()
            
            # Check for path traversal attempts
            if ".." in str(path):
                logger.warning(f"⚠️ Path traversal detected: {path_str}")
                return False
            
            # Check for system directories (basic protection)
            dangerous_dirs = ["C:\\Windows", "C:\\Program Files", "/etc", "/sys", "/proc"]
            for dangerous in dangerous_dirs:
                if str(path).startswith(dangerous):
                    logger.warning(f"⚠️ Access to system directory blocked: {path_str}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Path validation error: {e}")
            return False
    
    @staticmethod
    def is_safe_command(command):
        """
        Check if a system command is safe to execute.
        
        Args:
            command (str): Command to validate
            
        Returns:
            bool: True if command is safe
        """
        # Block dangerous commands
        dangerous_keywords = [
            "rm -rf", "del /f", "format", "rmdir /s",
            "drop table", "drop database",
            "sudo", "chmod 777"
        ]
        
        command_lower = command.lower()
        for keyword in dangerous_keywords:
            if keyword in command_lower:
                logger.warning(f"⚠️ Dangerous command blocked: {command}")
                return False
        
        return True
    
    @staticmethod
    def sanitize_input(text):
        """
        Sanitize user input text.
        
        Args:
            text (str): Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove control characters
        text = "".join(char for char in text if char.isprintable() or char.isspace())
        
        # Limit length
        max_length = 5000
        if len(text) > max_length:
            logger.warning(f"⚠️ Input truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]
        
        return text.strip()


class OutputValidator:
    """
    Validates and formats system outputs.
    """
    
    @staticmethod
    def format_response(text):
        """
        Format response text for consistency.
        
        Args:
            text (str): Response text
            
        Returns:
            str: Formatted text
        """
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    @staticmethod
    def is_valid_json(text):
        """
        Check if text is valid JSON.
        
        Args:
            text (str): Text to check
            
        Returns:
            bool: True if valid JSON
        """
        import json
        try:
            json.loads(text)
            return True
        except:
            return False
