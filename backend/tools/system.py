"""
System operation tools.

Provides functions for executing system commands and controlling the computer.
"""

import os
import platform
import subprocess
import datetime
import logging

logger = logging.getLogger(__name__)


def execute_command(command: str):
    """
    Executes a system command (Use with caution).
    
    Args:
        command (str): Shell command to execute
        
    Returns:
        str: Command output or error message
        
    Warning:
        This function executes arbitrary system commands and should be used carefully.
        
    Example:
        >>> result = execute_command("echo Hello")
        >>> print(result)
        'Hello'
    """
    try:
        logger.warning(f"⚠️ Executing system command: {command}")
        result = subprocess.check_output(command, shell=True, text=True, timeout=30)
        logger.info(f"✅ Command executed successfully")
        return result.strip()
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Command timed out: {command}")
        return "Error: Command timed out (30s limit)"
        
    except Exception as e:
        logger.error(f"❌ Error executing command: {e}")
        return f"Error executing command: {str(e)}"


def get_system_info():
    """
    Returns basic system information.
    
    Returns:
        dict: System information including OS, Release, Architecture, and Time
        
    Example:
        >>> info = get_system_info()
        >>> print(info['OS'])
        'Windows'
    """
    try:
        logger.info("ℹ️ Getting system information")
        info = {
            "OS": platform.system(),
            "Release": platform.release(),
            "Architecture": platform.machine(),
            "Time": datetime.datetime.now().strftime("%I:%M %p")
        }
        logger.info(f"✅ System info retrieved: {info['OS']} {info['Release']}")
        return info
        
    except Exception as e:
        logger.error(f"❌ Error getting system info: {e}")
        return {"error": str(e)}


def shutdown():
    """
    Shuts down the computer.
    
    Returns:
        str: Confirmation message
        
    Warning:
        This will actually shut down the computer after 5 seconds!
    """
    logger.warning("🛑 SHUTDOWN INITIATED")
    os.system("shutdown /s /t 5")
    return "Shutting down in 5 seconds..."


def restart():
    """
    Restarts the computer.
    
    Returns:
        str: Confirmation message
        
    Warning:
        This will actually restart the computer after 5 seconds!
    """
    logger.warning("🔄 RESTART INITIATED")
    os.system("shutdown /r /t 5")
    return "Restarting in 5 seconds..."
