# jarvis_ai/main.py
from core.agent import Agent
from voice.stt import Listener
from voice.tts import Speaker
from core.hud_server import HUDServer
import time

def main():
    try:
        listener = Listener()
        speaker = Speaker()
        jarvis = Agent()
        # wake_word = WakeWordDetector(listener) # REMOVED
        hud = HUDServer()
        
        print(f"🤖 {jarvis.state.current_state}: System initialized.")
        hud.start()
        hud.update_state("IDLE", "System Initialized")
        
        speaker.speak("Jarvis is ready. I am listening.")

        while True:
            # 1. Continuous Listen
            hud.update_state("LISTENING", "Listening...")
            user_input = listener.listen() 
            
            if not user_input or len(user_input) < 2:
                # Silence or noise
                time.sleep(0.1)
                continue

            print("YOU:", user_input)
            hud.update_state("THINKING", user_input)

            # 2. Process and Respond
            response = jarvis.run(user_input)
            print("JARVIS:", response)

            if response:
                hud.update_state("SPEAKING", response)
                speaker.speak(response)
            
            hud.update_state("IDLE", "Ready...")

    except KeyboardInterrupt:
        print("\n👋 Jarvis shutting down.")
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    main()
