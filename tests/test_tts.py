from voice.tts import Speaker

def test_tts():
    print("Testing TTS...")
    s = Speaker()
    s.speak("Hello sir, all systems operational.")

if __name__ == "__main__":
    test_tts()
