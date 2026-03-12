# jarvis_ai/core/state.py

class StateManager:
    VALID_STATES = {
        "IDLE",
        "LISTENING",
        "THINKING",
        "SPEAKING",
        "PLANNING",
        "EXECUTING",
        "ERROR"
    }

    def __init__(self):
        self.current_state = "IDLE"

    def set(self, new_state, message=None):
        if new_state not in self.VALID_STATES:
            print(f"[STATE] Unknown state: {new_state}")
            return

        self.current_state = new_state

        if message:
            print(f"[STATE] {new_state}: {message}")
        else:
            print(f"[STATE] {new_state}")
