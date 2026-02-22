# jarvis_ai/voice/voice_manager.py
"""
Central Coordinator for the Voice Subsystem.
Manages continuous listening, VAD state, sending chunks to STT, and TTS interruptions.
Supports both sync (threading) and async (asyncio) operation modes.
"""

import asyncio
import numpy as np
import logging
import threading

from voice.audio_stream import AudioStream
from voice.vad_engine import VADEngine
from voice.stt_engine import STTEngine
from voice.tts_engine import TTSEngine
from voice.interrupt_handler import InterruptHandler

logger = logging.getLogger(__name__)


class VoiceManager:
    """
    Central Coordinator for the Voice Subsystem.
    
    Sync mode: uses threading (for main.py CLI)
    Async mode: uses asyncio (for FastAPI WebSocket)
    """
    
    def __init__(self):
        logger.info("⚙️ Initializing Voice Manager...")
        self.stream = AudioStream()
        self.vad = VADEngine()
        self.stt = STTEngine()
        self.tts = TTSEngine()
        self.interrupt_handler = InterruptHandler(self.tts)
        
        # State tracking
        self.is_listening = False
        self.is_user_speaking = False
        self.speech_buffer = []
        self.silence_frames = 0
        self.silence_threshold = 15  # ~0.5-1.0s of silence to end turn
        
        self.on_speech_recognized = None  # Callback (sync or async)
        self._async_queue = None  # For async mode

    # ──────────────────────────────────────────────
    # Sync API (for main.py CLI usage)
    # ──────────────────────────────────────────────

    def start(self, on_speech_recognized_callback, mode="local"):
        """Starts the main background audio processing loop."""
        self.on_speech_recognized = on_speech_recognized_callback
        self.is_listening = True
        self.mode = mode
        
        if mode == "local":
            self.stream.start()
            threading.Thread(target=self._process_loop, daemon=True).start()
            logger.info("⚙️ Voice Manager active (sync local mode).")
        else:
            logger.info("⚙️ Voice Manager active (browser mode). Waiting for WS chunks.")

    def stop(self):
        """Stop listening and cleanup."""
        self.is_listening = False
        self.stream.stop()
        logger.info("⚙️ Voice Manager stopped.")

    def speak(self, text):
        """Proxy to TTSEngine. Blocks the calling thread."""
        self.tts.speak(text)

    # ──────────────────────────────────────────────
    # Async API (for FastAPI WebSocket usage)
    # ──────────────────────────────────────────────

    async def start_async(self):
        """Start listening and return an async queue that yields transcribed text."""
        self._async_queue = asyncio.Queue()
        self.is_listening = True
        self.stream.start()
        
        # Run the blocking process loop in a background thread
        loop = asyncio.get_event_loop()
        self.on_speech_recognized = lambda text: asyncio.run_coroutine_threadsafe(
            self._async_queue.put(text), loop
        )
        threading.Thread(target=self._process_loop, daemon=True).start()
        logger.info("⚙️ Voice Manager active (async mode).")
        return self._async_queue

    async def speak_async(self, text):
        """Non-blocking TTS for async contexts."""
        await self.tts.speak_async(text)

    async def get_next_utterance(self, timeout=None):
        """Wait for the next transcribed utterance from the mic."""
        if not self._async_queue:
            return None
        try:
            if timeout:
                return await asyncio.wait_for(self._async_queue.get(), timeout=timeout)
            return await self._async_queue.get()
        except asyncio.TimeoutError:
            return None

    # ──────────────────────────────────────────────
    # Internal processing (runs in background thread for both modes)
    # ──────────────────────────────────────────────

    def _process_loop(self):
        """Infinite loop reading from mic and passing to VAD."""
        while self.is_listening:
            chunk = self.stream.read_chunk(timeout=0.1)
            if chunk is None:
                continue

            is_speech = self.vad.is_speech(chunk)

            if is_speech:
                if not self.is_user_speaking:
                    logger.debug("🗣️ VAD: Speech Started")
                    self.is_user_speaking = True
                    self.interrupt_handler.handle_user_spoke()
                    self.speech_buffer = []

                self.silence_frames = 0
                self.speech_buffer.append(chunk)
            
            else:
                if self.is_user_speaking:
                    self.speech_buffer.append(chunk)
                    self.silence_frames += 1
                    
                    if self.silence_frames > self.silence_threshold:
                        logger.debug("🗣️ VAD: Speech Ended")
                        self.is_user_speaking = False
                        self._process_utterance()

    def _process_utterance(self):
        """Stitches the buffer and sends to STT."""
        if len(self.speech_buffer) < 5:
            self.speech_buffer = []
            return

        logger.info("🎙️ Processing Utterance...")
        
        audio_data = np.concatenate(self.speech_buffer, axis=0)
        self.speech_buffer = []

        # Run STT in a separate thread so we don't block VAD
        threading.Thread(target=self._run_stt_and_callback, args=(audio_data,), daemon=True).start()

    def _run_stt_and_callback(self, audio_data):
        """Run STT and fire the callback with the result."""
        text = self.stt.transcribe(audio_data)
        if text and self.on_speech_recognized:
            self.on_speech_recognized(text)

    def process_browser_chunk(self, chunk_bytes):
        """Process raw 16kHz Int16 audio from WebSocket."""
        if not self.is_listening:
            return

        chunk = np.frombuffer(chunk_bytes, dtype=np.int16)
        
        # Silero VAD prefers exact 512 chunks
        chunk_size = 512
        for i in range(0, len(chunk), chunk_size):
            subchunk = chunk[i:i+chunk_size]
            if len(subchunk) < chunk_size:
                subchunk = np.pad(subchunk, (0, chunk_size - len(subchunk)))

            is_speech = self.vad.is_speech(subchunk)

            if is_speech:
                if not self.is_user_speaking:
                    logger.debug("🗣️ VAD: Speech Started (Browser)")
                    self.is_user_speaking = True
                    self.interrupt_handler.handle_user_spoke()
                    self.speech_buffer = []

                self.silence_frames = 0
                self.speech_buffer.append(subchunk)
            
            else:
                if self.is_user_speaking:
                    self.speech_buffer.append(subchunk)
                    self.silence_frames += 1
                    
                    if self.silence_frames > self.silence_threshold:
                        logger.debug("🗣️ VAD: Speech Ended (Browser)")
                        self.is_user_speaking = False
                        self._process_utterance()
