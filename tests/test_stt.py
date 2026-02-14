from voice.stt import Listener

def test_stt():
    print("Testing STT...")
    l = Listener()
    print("Speak something...")
    text = l.listen()
    print(f"Captured: {text}")

if __name__ == "__main__":
    test_stt()
