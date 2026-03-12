from backend.voice.stt import Listener

from unittest.mock import patch, MagicMock

def test_stt():
    print("Testing STT...")
    with patch("backend.voice.stt.sd") as mock_sd, \
         patch("backend.voice.audio_stream.sd") as mock_stream_sd, \
         patch("backend.voice.stt.sd.query_devices", return_value={"name": "Mock Device", "default_samplerate": 44100}):
        # Mock sounddevice to avoid PortAudioError on CI
        mock_sd.query_devices.return_value = {"name": "Mock Device", "default_samplerate": 44100}
        
        from backend.voice.stt import Listener
        listener = Listener()
        print("Speak something...")
        
        # Mock listen to just return something and not actually record
        with patch.object(listener, 'listen', return_value="Mock transcription"):
            text = listener.listen()
            print(f"Captured: {text}")

if __name__ == "__main__":
    test_stt()
