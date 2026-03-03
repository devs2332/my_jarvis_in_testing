import os
import sys
import shutil

def check_python():
    print(f"🐍 Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("❌ Warning: Python 3.8+ is recommended.")
    else:
        print("✅ Python version suitable.")

def check_env():
    if os.path.exists(".env"):
        print("✅ .env file found.")
    else:
        print("❌ .env file missing! Run setup.py first.")

def check_dependencies():
    print("📦 Checking core dependencies...")
    try:
        import sounddevice
        import groq
        import faster_whisper
        import duckduckgo_search
        print("✅ Core dependencies found.")
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}. Run setup.py.")

def check_audio_devices():
    print("\n🎧 Checking Audio Devices...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        print(devices)
        print("\n💡 NOTE: Update 'MIC_DEVICE_INDEX' in 'voice/stt.py' with the ID of your microphone.")
    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")

def main():
    print("🩺 Jarvis Doctor - Environment Check\n" + "-"*30)
    check_python()
    check_env()
    check_dependencies()
    check_audio_devices()
    print("-" * 30 + "\n✅ Check complete.")

if __name__ == "__main__":
    main()
