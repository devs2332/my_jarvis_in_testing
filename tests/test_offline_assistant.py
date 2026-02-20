from voice.offline_assistant import (
    OfflineVoiceAssistant,
    AssistantState,
    StateMachine,
)


class FakeListener:
    def listen(self):
        return ""


class FakeSpeaker:
    def speak(self, _):
        return None


def test_state_machine_happy_path():
    sm = StateMachine()
    sm.transition(AssistantState.LISTENING)
    sm.transition(AssistantState.THINKING)
    sm.transition(AssistantState.SPEAKING)
    sm.transition(AssistantState.IDLE)
    assert sm.current_state == AssistantState.IDLE


def test_offline_assistant_memory_roundtrip():
    assistant = OfflineVoiceAssistant(listener=FakeListener(), speaker=FakeSpeaker())

    saved = assistant.process_text("remember buy milk")
    assert saved == "Saved: buy milk"

    recalled = assistant.process_text("what did i ask")
    assert recalled == "buy milk"
    assert assistant.state_machine.current_state == AssistantState.IDLE
