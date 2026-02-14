# jarvis_ai/voice/stt.py
import sounddevice as sd
from faster_whisper import WhisperModel
import numpy as np
import tempfile
import scipy.io.wavfile as wav
import os
import re
import time


class Listener:
    def __init__(self):
        print("🎧 Loading Whisper (accurate mode)...")

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
            "small",        # 🔥 better accuracy than base
            device="cpu",
            compute_type="int8"
        )

        print("✅ Whisper ready.")

    def listen(self):
        print("🎙️ Speak now...")

        audio = sd.rec(
            int(4 * self.sample_rate),   # longer window
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            device=self.device_index
        )
        sd.wait()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, self.sample_rate, audio)
            filename = f.name

        segments, info = self.model.transcribe(
            filename,
            language=None,        # AUTO: Hindi + English
            beam_size=3,
            vad_filter=True,
            temperature=0.3
        )

        os.remove(filename)

        text = " ".join(seg.text for seg in segments).strip()
        return self._normalize(text)

    def listen_command(self, seconds=4):
        # Silent listening for wake word or commands
        audio = sd.rec(
            int(seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            device=self.device_index
        )
        sd.wait()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wav.write(f.name, self.sample_rate, audio)
            filename = f.name

        try:
            segments, info = self.model.transcribe(
                filename,
                language="en",
                beam_size=3,
                vad_filter=True,
                temperature=0.3
            )
            text = " ".join(seg.text for seg in segments).strip()
            os.remove(filename)
            return self._normalize(text)
        except Exception as e:
            print(f"⚠️ STT Error: {e}")
            if os.path.exists(filename):
                os.remove(filename)
            return ""

    def _normalize(self, text):
        text = text.lower().strip()

        fillers = [
            "haan", "han", "hmm", "uh", "um",
            "achha", "accha", "please", "plz"
        ]

        for f in fillers:
            text = text.replace(f, "")

        replacements = {
            "kya hota hai": "",
            "kya hai": "",
            "batao": "",
            "samjhao": "",
            "samjha do": "",
            "explain karo": "explain",
            "you know what i mean": "",
            "you know what i mean?": "",
            "i'm feeling a little bit of a": "",
            "thank you": "",
            "tk you": "",
            }

        for k, v in replacements.items():
            text = text.replace(k, v)

        text = re.sub(r"\s+", " ", text).strip()
        return text

