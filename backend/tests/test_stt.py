from backend.voice.stt import Listener

def test_stt():
    print("Testing STT...")
    listener = Listener()
    print("Speak something...")
    text = listener.listen()
    print(f"Captured: {text}")

if __name__ == "__main__":
    test_stt()
