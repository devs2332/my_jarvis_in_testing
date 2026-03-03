# jarvis_ai/voice/tts_engine.py
import os
import asyncio
import logging
import edge_tts
from playsound import playsound
import threading

logger = logging.getLogger(__name__)

# Female voice options:
# "en-US-AriaNeural" - American female (warm and natural)
# "en-IN-NeerjaNeural" - Indian female (CURRENT)
VOICE = "en-IN-NeerjaNeural"


class TTSEngine:
    """Text-to-Speech Engine utilizing Edge-TTS with basic interruption support."""
    
    def __init__(self):
        self.voice = VOICE
        self.is_speaking = False
        self._current_audio_file = None
        logger.info(f"🔊 TTSEngine initialized (Voice: {self.voice})")

    def speak(self, text):
        """Synchronously blocks to speak text. Safe to call from any context (sync or async)."""
        if not text:
            return
            
        logger.info(f"🔊 SPEAKING: {text[:50]}...")
        self.is_speaking = True
        
        try:
            # Check if we're inside a running event loop (e.g. FastAPI)
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                # We're inside an async context — run TTS in a separate thread with its own loop
                result_event = threading.Event()
                def _run_in_thread():
                    try:
                        asyncio.run(self._generate_and_play(text))
                    finally:
                        result_event.set()
                t = threading.Thread(target=_run_in_thread, daemon=True)
                t.start()
                result_event.wait()  # Block until TTS finishes
            else:
                # Not inside async context — safe to use asyncio.run()
                asyncio.run(self._generate_and_play(text))
        except Exception as e:
            logger.error(f"❌ TTS ERROR: {e}")
        finally:
            self.is_speaking = False

    async def speak_async(self, text):
        """Async version for use inside FastAPI/WebSocket handlers."""
        if not text:
            return
        logger.info(f"🔊 SPEAKING (async): {text[:50]}...")
        self.is_speaking = True
        try:
            await self._generate_and_play(text)
        except Exception as e:
            logger.error(f"❌ TTS ERROR: {e}")
        finally:
            self.is_speaking = False

    def stop(self):
        """Attempts to stop current playback."""
        logger.info("🛑 TTS Interrupted by VAD")
        self.is_speaking = False

    async def _generate_and_play(self, text):
        filename = f"tts_{int(asyncio.get_event_loop().time() * 1000)}.mp3"
        self._current_audio_file = filename
        
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(filename)
            
            # Play only if we haven't been interrupted while generating
            if self.is_speaking:
                # Run blocking playsound in a thread to not block the event loop
                await asyncio.to_thread(playsound, filename)
                
        finally:
            self._current_audio_file = None
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

    async def generate_audio_bytes(self, text):
        """Generates TTS audio and returns bytes for streaming over WebSocket."""
        if not text:
            return b""
        filename = f"tts_{int(asyncio.get_event_loop().time() * 1000)}_ws.mp3"
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(filename)
            with open(filename, "rb") as f:
                audio_bytes = f.read()
            return audio_bytes
        except Exception as e:
            logger.error(f"❌ TTS ERROR: {e}")
            return b""
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

