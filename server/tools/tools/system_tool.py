"""
System information and control tools (safe mode).
"""

import platform
import logging
from typing import Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)


class SystemInfoInput(BaseModel):
    info_type: str = Field(
        default="overview",
        description="Type of info: 'overview', 'cpu', 'memory', 'disk'",
    )


class SystemInfoTool(BaseTool):
    name: str = "system_info"
    description: str = "Get system information like OS, CPU, memory, and disk usage."
    args_schema: Type[BaseModel] = SystemInfoInput

    async def _arun(self, info_type: str = "overview") -> str:
        """Get system information."""
        try:
            import psutil

            if info_type == "cpu":
                return (
                    f"CPU: {platform.processor()}\n"
                    f"Cores: {psutil.cpu_count(logical=False)} physical, "
                    f"{psutil.cpu_count(logical=True)} logical\n"
                    f"Usage: {psutil.cpu_percent(interval=1)}%"
                )
            elif info_type == "memory":
                mem = psutil.virtual_memory()
                return (
                    f"Total: {mem.total / (1024**3):.1f} GB\n"
                    f"Used: {mem.used / (1024**3):.1f} GB ({mem.percent}%)\n"
                    f"Available: {mem.available / (1024**3):.1f} GB"
                )
            elif info_type == "disk":
                disk = psutil.disk_usage("/")
                return (
                    f"Total: {disk.total / (1024**3):.1f} GB\n"
                    f"Used: {disk.used / (1024**3):.1f} GB ({disk.percent}%)\n"
                    f"Free: {disk.free / (1024**3):.1f} GB"
                )
            else:
                return (
                    f"OS: {platform.system()} {platform.release()}\n"
                    f"Machine: {platform.machine()}\n"
                    f"Python: {platform.python_version()}\n"
                    f"CPU: {platform.processor()}\n"
                    f"Cores: {psutil.cpu_count()}"
                )
        except ImportError:
            return f"OS: {platform.system()} {platform.release()} (psutil not installed for detailed info)"
        except Exception as e:
            return f"System info error: {e}"

    def _run(self, *args, **kwargs) -> str:
        return "Use async version"


class SystemControlInput(BaseModel):
    command: str = Field(description="Safe system command to execute")


class SystemControlTool(BaseTool):
    name: str = "system_control"
    description: str = (
        "Execute safe system commands. RESTRICTED — only approved "
        "commands are allowed. Enterprise plan only."
    )
    args_schema: Type[BaseModel] = SystemControlInput

    # Whitelist of safe commands
    SAFE_COMMANDS = {
        "date", "whoami", "hostname", "uptime",
        "ls", "dir", "pwd", "echo", "cat",
    }

    async def _arun(self, command: str) -> str:
        """Execute a safe system command."""
        import shlex
        parts = shlex.split(command)
        base_command = parts[0] if parts else ""

        if base_command not in self.SAFE_COMMANDS:
            return (
                f"Command '{base_command}' not in safe list. "
                f"Allowed: {', '.join(sorted(self.SAFE_COMMANDS))}"
            )

        try:
            import asyncio
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=10,
            )
            output = stdout.decode().strip()
            if stderr:
                output += f"\nSTDERR: {stderr.decode().strip()}"
            return output or "(no output)"
        except asyncio.TimeoutError:
            return "Command timed out (10s limit)"
        except Exception as e:
            return f"Execution error: {e}"

    def _run(self, *args, **kwargs) -> str:
        return "Use async version"
