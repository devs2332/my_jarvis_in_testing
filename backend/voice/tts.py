# jarvis_ai/voice/tts.py
"""
Text-to-Speech using Edge-TTS (Microsoft).

Provides natural-sounding speech synthesis with female voice using Edge-TTS.
"""

import os
import asyncio
import logging
import threading
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
        Convert text to speech and play it. Safe to call from any context.
        """
        if not text:
            logger.warning("Empty text provided to speaker")
            return

        logger.info(f"🔊 SPEAKING: {text[:50]}...")

        try:
            # Check if we're inside a running event loop (e.g. FastAPI)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # Inside async context — run in a separate thread with its own loop
                result_event = threading.Event()
                def _run_in_thread():
                    try:
                        asyncio.run(self._generate_and_play(text))
                    finally:
                        result_event.set()
                t = threading.Thread(target=_run_in_thread, daemon=True)
                t.start()
                result_event.wait()
            else:
                asyncio.run(self._generate_and_play(text))

        except Exception as e:
            logger.error(f"❌ TTS ERROR: {e}")
            print(f"❌ TTS ERROR: {e}")

    async def _generate_and_play(self, text):
        """
        Generate and play TTS audio (async method).
        """
        # Create unique filename
        filename = f"tts_{int(asyncio.get_event_loop().time() * 1000)}.mp3"

        try:
            # Generate speech using Edge-TTS
            logger.debug(f"Generating Edge-TTS audio for {len(text)} characters")
            
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(filename)

            # Play audio (in thread to not block event loop)
            logger.debug(f"Playing audio file: {filename}")
            await asyncio.to_thread(playsound, filename)

        finally:
            # Cleanup - always remove file
            if os.path.exists(filename):
                os.remove(filename)
                logger.debug(f"Cleaned up audio file: {filename}")

