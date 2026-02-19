"""
Voice module for Jarvis AI Assistant.

This package contains voice processing components:
- Listener: Speech-to-text using Whisper
- Speaker: Text-to-speech using gTTS
- WakeWordDetector: Wake word detection
"""

from voice.stt import Listener
from voice.tts import Speaker


__all__ = [
    'Listener',
    'Speaker',
]
