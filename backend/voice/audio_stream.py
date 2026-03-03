# jarvis_ai/voice/audio_stream.py
import sounddevice as sd
import numpy as np
import queue
import logging

logger = logging.getLogger(__name__)

class AudioStream:
    """Handles real-time continuous microphone streaming."""
    
    def __init__(self, sample_rate=16000, chunk_size=512):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.stream = None
        
        # Auto-detect default mic
        try:
            default_device = sd.query_devices(kind='input')
            self.device_index = default_device['index']
            logger.info(f"🎤 AudioStream using: {default_device['name']}")
        except Exception as e:
            logger.warning(f"⚠️ Could not auto-detect mic: {e}. Using fallback 1.")
            self.device_index = 1
            
    def _audio_callback(self, indata, frames, time, status):
        """Called for each audio block by sounddevice."""
        if status:
            logger.warning(f"Audio status: {status}")
        # Put a copy of the incoming audio to the queue
        self.audio_queue.put(indata.copy())
        
    def start(self):
        """Start the continuous audio stream."""
        if self.stream is not None:
            return
            
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size,
            device=self.device_index,
            callback=self._audio_callback
        )
        self.stream.start()
        logger.info("🎙️ Audio stream started.")
        
    def stop(self):
        """Stop the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            logger.info("🛑 Audio stream stopped.")
            
    def read_chunk(self, block=True, timeout=None):
        """Read the next chunk of audio from the queue."""
        try:
            return self.audio_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
            
    def clear_queue(self):
        """Empty the current buffer."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
