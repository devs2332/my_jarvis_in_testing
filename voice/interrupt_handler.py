# jarvis_ai/voice/interrupt_handler.py
import logging
from voice.tts_engine import TTSEngine

logger = logging.getLogger(__name__)

class InterruptHandler:
    """Monitors VAD and interrupts active operations (like TTS)."""
    
    def __init__(self, tts_engine: TTSEngine):
        self.tts = tts_engine
        
    def handle_user_spoke(self):
        """Called when the VAD engine detects user speech."""
        if self.tts.is_speaking:
            logger.info("⚡ barge-in detected! Stopping TTS playback.")
            self.tts.stop()
            # In a fully robust system, you would also clear the TTS queue here
            return True # Interruption occurred
        return False # No interruption needed
