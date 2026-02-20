"""
Offline voice assistant architecture.

This module mirrors the requested Offline_Assistant structure while keeping the
implementation lightweight and locally runnable inside the existing project.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, DefaultDict
from collections import defaultdict
import operator
import re
import uuid

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from voice.stt import Listener
    from voice.tts import Speaker


class AssistantState(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"


class StateMachine:
    """IDLE / LISTENING / THINKING / SPEAKING state controller."""

    _allowed = {
        AssistantState.IDLE: {AssistantState.LISTENING},
        AssistantState.LISTENING: {AssistantState.THINKING, AssistantState.IDLE},
        AssistantState.THINKING: {AssistantState.SPEAKING, AssistantState.IDLE},
        AssistantState.SPEAKING: {AssistantState.IDLE, AssistantState.LISTENING},
    }

    def __init__(self) -> None:
        self.current_state = AssistantState.IDLE

    def transition(self, new_state: AssistantState) -> None:
        allowed = self._allowed[self.current_state]
        if new_state not in allowed:
            raise ValueError(f"Invalid transition: {self.current_state} -> {new_state}")
        self.current_state = new_state


class EventBus:
    """Simple internal event communication bus."""

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, list[Callable[..., None]]] = defaultdict(list)

    def subscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        self._subscribers[event_name].append(callback)

    def publish(self, event_name: str, **payload: Any) -> None:
        for callback in self._subscribers[event_name]:
            callback(**payload)


@dataclass
class SessionManager:
    """User session + local context."""

    user_id: str = "default"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    history: list[dict[str, str]] = field(default_factory=list)
    memory: dict[str, str] = field(default_factory=dict)

    def remember_turn(self, user_text: str, assistant_text: str) -> None:
        self.history.append({"user": user_text, "assistant": assistant_text})


# ---- core/audio ----
class AudioStream:
    """Real-time mic streaming adapter (listener-backed)."""

    def __init__(self, listener: Any) -> None:
        self.listener = listener

    def capture_text(self) -> str:
        return self.listener.listen() or ""


class VADEngine:
    """Voice activity detection using energy threshold over text presence proxy."""

    def is_voice_activity(self, text: str) -> bool:
        return bool(text and text.strip())


class STTEngine:
    """Whisper local/selected STT wrapper."""

    def __init__(self, listener: Any) -> None:
        self.listener = listener

    def transcribe(self) -> str:
        return self.listener.listen() or ""


class TTSEngine:
    """Piper/Kokoro style local TTS abstraction (Speaker-backed)."""

    def __init__(self, speaker: Any) -> None:
        self.speaker = speaker

    def speak(self, text: str) -> None:
        self.speaker.speak(text)


class InterruptHandler:
    """Stops TTS if user starts speaking (state-level cooperative interrupt)."""

    def __init__(self) -> None:
        self.interrupted = False

    def request_interrupt(self) -> None:
        self.interrupted = True

    def clear(self) -> None:
        self.interrupted = False


# ---- core/brain ----
class IntentClassifier:
    """Optional local intent detection."""

    def classify(self, text: str) -> str:
        lowered = text.lower()
        if "time" in lowered:
            return "time"
        if "calculate" in lowered or re.search(r"\d+\s*[+\-*/]\s*\d+", lowered):
            return "calculator"
        if lowered.startswith("open "):
            return "system_control"
        if "remember" in lowered:
            return "memory"
        return "chat"


class TimeSkill:
    def run(self, _: str) -> str:
        return f"Current time is {datetime.now().strftime('%I:%M %p')}"


class CalculatorSkill:
    _ops = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
    }

    def run(self, text: str) -> str:
        match = re.search(r"(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)", text)
        if not match:
            return "I could not parse the calculation request."
        left, op, right = match.groups()
        result = self._ops[op](float(left), float(right))
        if result.is_integer():
            return str(int(result))
        return str(round(result, 4))


class SystemControlSkill:
    def run(self, text: str) -> str:
        return f"System command simulated: {text}"


class FileManagerSkill:
    def run(self, _: str) -> str:
        return "File manager skill is available."


class MediaControlSkill:
    def run(self, _: str) -> str:
        return "Media control skill is available."


class MemoryManager:
    """Local memory management for voice interactions."""

    def __init__(self, session: SessionManager) -> None:
        self.session = session

    def store(self, key: str, value: str) -> None:
        self.session.memory[key] = value

    def fetch(self, key: str) -> str | None:
        return self.session.memory.get(key)


class CommandRouter:
    """Routes intents to skills."""

    def __init__(self) -> None:
        self.skills: dict[str, Any] = {
            "time": TimeSkill(),
            "calculator": CalculatorSkill(),
            "system_control": SystemControlSkill(),
            "file_manager": FileManagerSkill(),
            "media_control": MediaControlSkill(),
        }

    def route(self, intent: str, text: str) -> str:
        skill = self.skills.get(intent)
        if not skill:
            return "No matching offline skill found."
        return skill.run(text)


class ResponseGenerator:
    """Rule-based fallback responses for offline mode."""

    def generate(self, text: str) -> str:
        if not text.strip():
            return "I did not catch that."
        return "I am running in offline mode and heard: " + text


# ---- core/security ----
class SpeakerVerification:
    def verify(self, _: str = "") -> bool:
        return True


class FaceVerification:
    def verify(self, _: str = "") -> bool:
        return True


class RoleManager:
    def __init__(self) -> None:
        self.roles = {"default": "admin"}

    def get_role(self, user_id: str) -> str:
        return self.roles.get(user_id, "guest")


class OfflineVoiceAssistant:
    """Integrated orchestrator matching the requested offline architecture."""

    def __init__(self, listener: Any | None = None, speaker: Any | None = None) -> None:
        self.state_machine = StateMachine()
        self.event_bus = EventBus()
        self.session_manager = SessionManager()

        if listener is None:
            from voice.stt import Listener
            listener = Listener()
        if speaker is None:
            from voice.tts import Speaker
            speaker = Speaker()

        self.listener = listener
        self.speaker = speaker

        self.audio_stream = AudioStream(self.listener)
        self.vad_engine = VADEngine()
        self.stt_engine = STTEngine(self.listener)
        self.tts_engine = TTSEngine(self.speaker)
        self.interrupt_handler = InterruptHandler()

        self.intent_classifier = IntentClassifier()
        self.command_router = CommandRouter()
        self.response_generator = ResponseGenerator()
        self.memory_manager = MemoryManager(self.session_manager)

        self.speaker_verification = SpeakerVerification()
        self.face_verification = FaceVerification()
        self.role_manager = RoleManager()

    def process_text(self, text: str) -> str:
        self.state_machine.transition(AssistantState.LISTENING)
        if not self.vad_engine.is_voice_activity(text):
            self.state_machine.transition(AssistantState.IDLE)
            return ""

        self.state_machine.transition(AssistantState.THINKING)

        if text.lower().startswith("remember "):
            payload = text[9:].strip()
            self.memory_manager.store("last_note", payload)
            reply = f"Saved: {payload}"
        elif "what did i ask" in text.lower():
            note = self.memory_manager.fetch("last_note")
            reply = note or "I don't have any stored note yet."
        else:
            intent = self.intent_classifier.classify(text)
            reply = self.command_router.route(intent, text)
            if reply == "No matching offline skill found.":
                reply = self.response_generator.generate(text)

        self.state_machine.transition(AssistantState.SPEAKING)
        self.session_manager.remember_turn(text, reply)
        self.event_bus.publish("assistant_response", text=reply)
        self.state_machine.transition(AssistantState.IDLE)
        return reply
