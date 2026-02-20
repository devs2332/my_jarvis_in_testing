# jarvis_ai/voice/vad_engine.py
import torch
import numpy as np
import logging
import os
import urllib.request

logger = logging.getLogger(__name__)

class VADEngine:
    """Voice Activity Detection using Silero VAD for highly accurate speech detection."""
    
    def __init__(self, sample_rate=16000, threshold=0.5):
        self.sample_rate = sample_rate
        self.threshold = threshold
        
        logger.info("🧠 Initializing VAD Engine (Silero)...")
        self.model, utils = torch.hub.load(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
        self.model.eval()
        self.get_speech_timestamps = utils[0]
        logger.info("✅ VAD Engine ready.")

    def is_speech(self, audio_chunk_int16):
        """
        Takes a chunk of int16 audio (e.g. from AudioStream),
        converts to float32 tensor, and returns True if speech is detected.
        """
        # Convert int16 -> float32 between -1.0 and 1.0 (expected by Silero)
        audio_float32 = audio_chunk_int16.astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_float32).squeeze()
        
        # Make sure tensor is 1D
        if audio_tensor.ndim > 1:
            audio_tensor = audio_tensor.mean(dim=1)
            
        with torch.no_grad():
            confidence = self.model(audio_tensor, self.sample_rate).item()
            
        return confidence > self.threshold
