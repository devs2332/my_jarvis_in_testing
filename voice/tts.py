# jarvis_ai/voice/tts.py
"""
Text-to-Speech using Edge-TTS (Microsoft).

Provides natural-sounding speech synthesis with female voice using Edge-TTS.
"""

import os
import asyncio
import logging
import edge_tts
from playsound import playsound

logger = logging.getLogger(__name__)

# Female voice options (pick one):
# "en-US-AriaNeural" - American female (warm and natural)
# "en-GB-SoniaNeural" - British female (clear and professional)
# "en-AU-NatashaNeural" - Australian female
# "en-IN-NeerjaNeural" - Indian female (CURRENT)
VOICE = "en-IN-NeerjaNeural"


class Speaker:
    """
    Text-to-Speech speaker using Edge-TTS.
    
    Generates natural-sounding audio from text using Microsoft Edge's TTS engine.
    Uses a female voice for more pleasant interaction.
    """
    
    def __init__(self):
        """Initialize the Edge-TTS speaker."""
        self.voice = VOICE
        logger.info(f"🔊 Edge-TTS Speaker initialized (Female voice: {self.voice})")
        print(f"🔊 Edge-TTS Speaker initialized (Female voice: {self.voice})")

    def speak(self, text):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to convert to speech
            
        Example:
            >>> speaker = Speaker()
            >>> speaker.speak("Hello, how are you?")
        """
        if not text:
            logger.warning("Empty text provided to speaker")
            return

        logger.info(f"🔊 SPEAKING: {text[:50]}...")

        try:
            # Run async TTS generation
            asyncio.run(self._generate_and_play(text))

        except Exception as e:
            logger.error(f"❌ TTS ERROR: {e}")
            print(f"❌ TTS ERROR: {e}")

    async def _generate_and_play(self, text):
        """
        Generate and play TTS audio (async method).
        
        Args:
            text (str): Text to synthesize
        """
        # Create unique filename
        filename = f"tts_{int(asyncio.get_event_loop().time() * 1000)}.mp3"

        try:
            # Generate speech using Edge-TTS
            logger.debug(f"Generating Edge-TTS audio for {len(text)} characters")
            
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(filename)

            # Play audio (blocking until finished)
            logger.debug(f"Playing audio file: {filename}")
            playsound(filename)

        finally:
            # Cleanup - always remove file
            if os.path.exists(filename):
                os.remove(filename)
                logger.debug(f"Cleaned up audio file: {filename}")
