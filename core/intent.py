# jarvis_ai/core/intent.py
def detect_intent(text: str):
    text = text.lower().strip()

    # SAVE MEMORY (explicit command only)
    if text.startswith("remember "):
        return "MEMORY_SAVE"

    # RECALL MEMORY
    if any(x in text for x in [
        "what is my name",
        "mera naam kya",
        "my name",
        "tell me my name"
    ]):
        return "MEMORY_RECALL"

    return "CHAT"
