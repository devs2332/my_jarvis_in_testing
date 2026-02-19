# jarvis_ai/voice/stt.py
import sounddevice as sd
from faster_whisper import WhisperModel
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import os
import re
import time
from groq import Groq
from config import STT_ENGINE

class Listener:
    def __init__(self):
        print("🎧 Initializing Speech Recognition...")
        
        # 1. Setup Groq
        self.groq_client = None
        if STT_ENGINE == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                try:
                    self.groq_client = Groq(api_key=api_key)
                    print("✅ Groq Whisper API ready (Primary).")
                except Exception as e:
                    print(f"⚠️ Groq Init Failed: {e}")
            else:
                print("⚠️ No GROQ_API_KEY found.")

        # 2. Setup SpeechBrain (If selected)
        self.sb_model = None
        if STT_ENGINE == "speechbrain":
            print("🎧 Loading SpeechBrain (might download model on first run)...")
            try:
                from speechbrain.inference.ASR import EncoderDecoderASR
                self.sb_model = EncoderDecoderASR.from_hparams(
                    source="speechbrain/asr-crdnn-rnnlm-librispeech", 
                    savedir="pretrained_models/speechbrain-crdnn-rnnlm-librispeech",
                    run_opts={"device": "cpu"} # Force CPU to avoid CUDA version mismatch crashes
                )
                print("✅ SpeechBrain ready (Primary).")
            except Exception as e:
                print(f"⚠️ SpeechBrain Init Failed: {e}. Falling back to default.")

        # 3. Setup Local Faster-Whisper (Always load as reliable core)
        if not self.groq_client and not self.sb_model: # Only print if it's the active fallback
             print(f"🎧 Loading Local Whisper (Engine: {STT_ENGINE})...")
        
        # Auto-detect microphone
        try:
            default_device = sd.query_devices(kind='input')
            MIC_DEVICE_INDEX = default_device['index']
            print(f"🎤 Auto-detected Default Mic: {default_device['name']} (Index: {MIC_DEVICE_INDEX})")
        except Exception as e:
            print(f"⚠️ Could not auto-detect mic: {e}. Using fallback index 1.")
            MIC_DEVICE_INDEX = 1

        sd.default.device = (MIC_DEVICE_INDEX, None)
        device_info = sd.query_devices(MIC_DEVICE_INDEX)
        self.sample_rate = int(device_info["default_samplerate"])
        self.device_index = MIC_DEVICE_INDEX
        print(f"🎤 Using mic: {device_info['name']}")

        self.model = WhisperModel(
            "small",        # Balanced Open Source Model
            device="cpu",
            compute_type="int8"
        )
        print("✅ Local Whisper ready.")

    def listen(self, timeout=None):
        """
        Records audio and transcribes it.
        Return: transcribed text (str) or ""
        """
        print("🎙️ Listening...")
        
        # Record audio
        duration = 5 # default seconds
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            device=self.device_index
        )
        sd.wait()

        # Check if audio is silent (basic VAD)
        # simplistic energy check
        rms = np.sqrt(np.mean(audio**2))
        if rms < 100: # Threshold for silence requires tuning
            # print("Silence detected.")
            return ""

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, self.sample_rate, audio)
            filename = f.name

        try:
            text = self._transcribe(filename)
            return self._normalize(text)
        finally:
            if os.path.exists(filename):
                os.remove(filename)

    def _transcribe(self, filename):
        """Use Groq, SpeechBrain, or Local Whisper based on config."""
        
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
                print(f"⚠️ Groq STT Failed: {e}. Switching to local.")

        # 2. Try SpeechBrain
        if STT_ENGINE == "speechbrain" and self.sb_model:
            try:
                # SpeechBrain ASR transcription
                transcription = self.sb_model.transcribe_file(filename)
                return transcription
            except Exception as e:
                print(f"⚠️ SpeechBrain STT Failed: {e}. Switching to local.")

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
        if text in ["you", "thank you", "bye", "watching"]:
            return ""

        text = re.sub(r"\s+", " ", text).strip()
        return text
