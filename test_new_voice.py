# Test Edge-TTS Female Voice
import asyncio
from voice.tts import Speaker

def test_female_voice():
    print("Testing new Edge-TTS female voice...")
    speaker = Speaker()
    
    # Test with a sample sentence
    speaker.speak("Hello! I am Jarvis with a new natural female voice. How do I sound?")
    print("✅ Voice test complete!")

if __name__ == "__main__":
    test_female_voice()
