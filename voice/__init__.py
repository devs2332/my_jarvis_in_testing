"""Voice module for Jarvis AI Assistant."""

from voice.offline_assistant import OfflineVoiceAssistant

__all__ = ["Listener", "Speaker", "OfflineVoiceAssistant"]


def __getattr__(name):
    if name == "Listener":
        from voice.stt import Listener

        return Listener
    if name == "Speaker":
        from voice.tts import Speaker

        return Speaker
    raise AttributeError(name)
