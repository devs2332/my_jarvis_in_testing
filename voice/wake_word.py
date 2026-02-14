# jarvis_ai/voice/wake_word.py
"""
Wake word detection for Jarvis.

Listens for the wake word "Jarvis" to activate the assistant.
"""

import logging

logger = logging.getLogger(__name__)

WAKE_WORD = "jarvis"


class WakeWordDetector:
    """
    Detects the wake word in audio input.
    
    Continuously listens for the wake word to activate the assistant.
    Includes phonetic fallback matching for similar-sounding words.
    
    Attributes:
        listener: STT Listener instance for audio transcription
    """
    
    def __init__(self, listener):
        """
        Initialize the wake word detector.
        
        Args:
            listener: Listener instance for speech-to-text
        """
        self.listener = listener
        logger.info(f"Wake word detector initialized (wake word: '{WAKE_WORD}')")

    def wait_for_wake_word(self):
        """
        Wait until the wake word is detected.
        
        Blocks until "Jarvis" or a phonetically similar word is heard.
        Uses fallback matching to handle transcription variations.
        """
        logger.info("🟡 Waiting for wake word...")
        print("🟡 Say 'Jarvis'...")
        
        while True:
            text = self.listener.listen_command(seconds=3).lower()
            
            if text:
                logger.debug(f"👂 Heard: '{text}'")
                print(f"👂 Heard: '{text}'")
            
            if WAKE_WORD in text:
                logger.info(f"🟢 Wake word detected: {text}")
                print(f"🟢 Wake word detected: {text}")
                return
            
            # Fallback for similar sounding words (Phonetic matching)
            fallbacks = ["job is", "javis", "jabis", "service", "harvest", "travis"]
            if any(f in text for f in fallbacks):
                logger.info(f"🟢 Wake word detected (fallback): {text}")
                print(f"🟢 Wake word detected (fallback): {text}")
                return
