# jarvis_ai/main.py
from core.agent import Agent
from voice.stt import Listener
from voice.tts import Speaker
from voice.wake_word import WakeWordDetector
from core.hud_server import HUDServer

def main():
    try:
        listener = Listener()
        speaker = Speaker()
        jarvis = Agent()
        wake_word = WakeWordDetector(listener)
        hud = HUDServer()
        
        print(f"🤖 {jarvis.state.current_state}: System initialized.")
        hud.start()
        hud.update_state("IDLE", "System Initialized")
        
        speaker.speak("Jarvis is ready. Say Jarvis to wake me up.")

        while True:
            # 1. Wait for Wake Word
            hud.update_state("IDLE", "Waiting for Wake Word...")
            wake_word.wait_for_wake_word()
            
            # 2. Wake up response
            hud.update_state("LISTENING", "Yes sir?")
            speaker.speak("Yes sir?")
            
            # 3. Listen for command
            print("🔴 Listening for command...")
            hud.update_state("LISTENING", "Listening...")
            user_input = listener.listen() # Default 4 seconds
            
            if not user_input:
                print("❌ No input detected.")
                continue

            print("YOU:", user_input)
            hud.update_state("THINKING", user_input)

            # 4. Process and Respond
            response = jarvis.run(user_input)
            print("JARVIS:", response)

            if response:
                hud.update_state("SPEAKING", response)
                speaker.speak(response)
            
            print("💤 Going back to sleep...")
            hud.update_state("IDLE", "Sleeping...")

    except KeyboardInterrupt:
        print("\n👋 Jarvis shutting down.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()
