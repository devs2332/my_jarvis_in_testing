"""
Prompt injection protection layer.
Detects and sanitizes potentially malicious prompt injection attempts.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?prior\s+(instructions|rules|guidelines)",
    r"forget\s+(everything|all)\s+(above|before|prior)",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"new\s+instructions?\s*:",
    r"system\s*prompt\s*:",
    r"override\s+(system|safety|security)",
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode\s+(enabled|activated|on)",
    r"\[SYSTEM\]",
    r"\[INST\]",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"<\|system\|>",
    r"```system",
]

# Compiled patterns for efficiency
_compiled_patterns = [
    re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS
]


def detect_injection(text: str) -> tuple[bool, list[str]]:
    """
    Check text for prompt injection patterns.
    Returns (is_malicious, matched_patterns).
    """
    matches = []
    for pattern in _compiled_patterns:
        if pattern.search(text):
            matches.append(pattern.pattern)

    return len(matches) > 0, matches


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potential injection attempts.
    Returns cleaned text.
    """
    is_malicious, matches = detect_injection(text)

    if is_malicious:
        logger.warning(
            f"Prompt injection detected! Patterns: {matches}"
        )
        # Remove matched patterns
        cleaned = text
        for pattern in _compiled_patterns:
            cleaned = pattern.sub("[FILTERED]", cleaned)
        return cleaned

    # Basic sanitization
    text = text.strip()
    # Remove null bytes
    text = text.replace("\x00", "")
    # Limit length
    if len(text) > 10000:
        text = text[:10000]

    return text


def is_safe_tool_call(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """
    Validate whether a tool call is safe to execute.
    Returns (is_safe, reason).
    """
    # Block dangerous system commands
    dangerous_commands = [
        "rm -rf", "del /f", "format", "shutdown",
        "mkfs", "dd if=", ":(){ :|:& };:",
    ]

    input_str = str(tool_input).lower()
    for cmd in dangerous_commands:
        if cmd in input_str:
            return False, f"Blocked dangerous command: {cmd}"

    return True, "ok"
