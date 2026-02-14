print("STEP 1: Script started")

from faster_whisper import WhisperModel
print("STEP 2: faster-whisper imported")

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os

print("STEP 3: audio libs imported")

print("STEP 4: Loading Whisper model...")
model = WhisperModel("base", device="cpu", compute_type="int8")
print("STEP 5: Whisper model loaded")

print("STEP 6: Recording 3 seconds... Speak now")
audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1, dtype="int16")
sd.wait()
print("STEP 7: Recording done")

with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
    wav.write(f.name, 16000, audio)
    filename = f.name

print("STEP 8: Transcribing...")
segments, _ = model.transcribe(filename, language="en")

text = " ".join(seg.text for seg in segments)
print("STEP 9: TRANSCRIPTION RESULT:")
print(text)

os.remove(filename)
print("STEP 10: Done")
