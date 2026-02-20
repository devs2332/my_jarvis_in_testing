# jarvis_ai/voice/stt_engine.py
from faster_whisper import WhisperModel
import tempfile
import scipy.io.wavfile as wav
import os
import re
import logging
from groq import Groq
from config import STT_ENGINE

logger = logging.getLogger(__name__)

class STTEngine:
    """Speech-to-Text Engine incorporating Whisper, SpeechBrain, and Groq."""
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        logger.info("🎧 Initializing Speech Recognition...")
        
        # 1. Setup Groq
        self.groq_client = None
        if STT_ENGINE == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.groq_client = Groq(api_key=api_key)
                    logger.info("✅ Groq Whisper API ready (Primary).")
                except Exception as e:
                    logger.warning(f"⚠️ Groq Init Failed: {e}")
            else:
                logger.warning("⚠️ No GROQ_API_KEY found.")

        # 2. Setup SpeechBrain
        self.sb_model = None
        if STT_ENGINE == "speechbrain":
            logger.info("🎧 Loading SpeechBrain (might download model on first run)...")
            try:
                from speechbrain.inference.ASR import EncoderDecoderASR
                self.sb_model = EncoderDecoderASR.from_hparams(
                    source="speechbrain/asr-crdnn-rnnlm-librispeech", 
                    savedir="pretrained_models/speechbrain-crdnn-rnnlm-librispeech",
                    run_opts={"device": "cpu"}
                )
                logger.info("✅ SpeechBrain ready (Primary).")
            except Exception as e:
                logger.warning(f"⚠️ SpeechBrain Init Failed: {e}. Falling back to default.")

        # 3. Local Faster-Whisper (Always load as reliable core fallback)
        if not self.groq_client and not self.sb_model:
             logger.info(f"🎧 Loading Local Whisper (Engine: {STT_ENGINE})...")
        
        self.model = WhisperModel(
            "small",        # Balanced Open Source Model
            device="cpu",
            compute_type="int8"
        )
        logger.info("✅ Local Whisper ready.")

    def transcribe(self, audio_data_int16):
        """
        Transcribes an array of raw audio data into text.
        Args:
            audio_data_int16 (np.array): Raw int16 PCM audio.
        """
        if len(audio_data_int16) == 0:
            return ""

        # Save to temp file since APIs/models expect file paths or bytes streams containing WAV headers
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, self.sample_rate, audio_data_int16)
            filename = f.name

        try:
            text = self._transcribe_file(filename)
            return self._normalize(text)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def _transcribe_file(self, filename):
        """Internal router to use Groq, SpeechBrain, or Local Whisper based on config."""
        # 1. Try Groq
        if STT_ENGINE == "groq" and self.groq_client:
            try:
                with open(filename, "rb") as file:
                    transcription = self.groq_client.audio.transcriptions.create(
                        file=(filename, file.read()),
                        model="whisper-large-v3",
                        response_format="text",
                        language="en", 
                        temperature=0.0
                    )
                return transcription
            except Exception as e:
                logger.warning(f"⚠️ Groq STT Failed: {e}. Switching to local.")

        # 2. Try SpeechBrain
        if STT_ENGINE == "speechbrain" and self.sb_model:
            try:
                transcription = self.sb_model.transcribe_file(filename)
                return transcription
            except Exception as e:
                logger.warning(f"⚠️ SpeechBrain STT Failed: {e}. Switching to local.")

        # 3. Local Faster-Whisper (Default / Fallback)
        segments, info = self.model.transcribe(
            filename,
            beam_size=5,
            vad_filter=True
        )
        return " ".join(seg.text for seg in segments).strip()

    def _normalize(self, text):
        if not text: return ""
        text = text.lower().strip()
        
        # Remove hallucinations / common whisper failures
        if text in ["you", "thank you.", "thank you", "bye", "watching", "thanks for watching!", "thanks.", "thanks"]:
            return ""

        text = re.sub(r"\s+", " ", text).strip()
        return text

    async def transcribe_async(self, audio_data_int16):
        """
        Async wrapper for transcribe() — runs blocking STT in a thread pool.
        Use this in FastAPI/WebSocket handlers to avoid blocking the event loop.
        """
        import asyncio
        return await asyncio.to_thread(self.transcribe, audio_data_int16)

