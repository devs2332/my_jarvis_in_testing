# jarvis_ai/core/intent_router.py
import re
from datetime import datetime

class IntentRouter:
    def __init__(self, memory):
        self.memory = memory

    def route(self, text: str):
        text = text.lower().strip()

        # ---------- MEMORY SAVE ----------
        # ---------- MEMORY SAVE ----------
        # 1. Name
        name_match = re.search(r"(my name is|mera naam|name is)\s+(\w+)", text)
        if name_match:
            name = name_match.group(2)
            self.memory.set("name", name)
            return f"Okay, I will remember your name is {name}.", "memory"

        # 2. Generic Remember "remember that sky is blue" -> key=sky, value=blue (simplified)
        # Or just "remember [message]" -> store in a list? 
        # For now, let's stick to simple key-value if possible, or just exact phrase storage
        # "Remember that Delhi is capital"
        remember_match = re.search(r"remember that\s+(.+)", text)
        if remember_match:
            info = remember_match.group(1)
            self.memory.set(f"fact_{int(datetime.now().timestamp())}", info)
            return f"Okay, I have stored: '{info}'", "memory"

        # ---------- MEMORY RECALL ----------
        if any(q in text for q in [
            "what is my name",
            "mera naam kya hai",
            "tell me my name",
            "my name"
        ]):
            name = self.memory.get("name")
            if name:
                return f"Your name is {name}.", "memory"
            else:
                return "I don't know your name yet. You can tell me.", "memory"

        # ---------- DATE / TIME (FAST TOOL) ----------
        if any(q in text for q in [
            "date", "today", "aaj ki date"
        ]):
            today = datetime.now().strftime("%d %B %Y")
            return f"Today's date is {today}.", "tool"

        if any(q in text for q in [
            "time", "samay", "kitna baje"
        ]):
            now = datetime.now().strftime("%I:%M %p")
            return f"The time is {now}.", "tool"

        # ---------- BROWSER TOOLS ----------
        if "open" in text and ("google" in text or "youtube" in text or "site" in text):
            from tools.browser import open_url
            if "google" in text:
                return open_url("google.com"), "tool"
            elif "youtube" in text:
                return open_url("youtube.com"), "tool"
            else:
                 # Extract URL roughly (improvement needed for robust extraction)
                 words = text.split()
                 for w in words:
                     if "." in w:
                         return open_url(w), "tool"
        
        # ---------- SYSTEM TOOLS ----------
        if "shutdown" in text:
            from tools.system import shutdown
            return shutdown(), "tool"
            
        if "restart" in text:
            from tools.system import restart
            return restart(), "tool"

        # ---------- FALLBACK TO LLM ----------
        return None, "llm"
