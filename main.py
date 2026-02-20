# jarvis_ai/main.py
from core.agent import Agent
from voice.voice_manager import VoiceManager
from core.hud_server import HUDServer
import time
import queue

def main():
    try:
        # We use a queue to pass recognized speech from the VoiceManager thread back to the main thread
        speech_queue = queue.Queue()
        
        def on_speech_recognized(text):
            speech_queue.put(text)

        voice = VoiceManager()
        jarvis = Agent()
        hud = HUDServer()
        
        print(f"🤖 {jarvis.state.current_state}: System initialized.")
        hud.start()
        hud.update_state("IDLE", "System Initialized")
        
        # Start the background voice pipeline
        voice.start(on_speech_recognized_callback=on_speech_recognized)
        voice.speak("Jarvis is ready. I am listening.")

        while True:
            hud.update_state("LISTENING", "Listening...")
            
            # Block until speech is recognized by the background STT thread
            try:
                user_input = speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            if not user_input or len(user_input) < 2:
                continue

            print("YOU:", user_input)
            hud.update_state("THINKING", user_input)

            # Process and Respond
            response = jarvis.run(user_input)
            print("JARVIS:", response)

            if response:
                hud.update_state("SPEAKING", response)
                voice.speak(response)
            
            hud.update_state("IDLE", "Ready...")

    except KeyboardInterrupt:
        print("\n👋 Jarvis shutting down.")
        if 'voice' in locals():
            voice.stop()
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        if 'voice' in locals():
            voice.stop()

if __name__ == "__main__":
    main()
