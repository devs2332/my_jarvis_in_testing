"""
Interactive setup wizard for Jarvis AI.

Guides users through configuration and setup process.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version is sufficient."""
    print("[1/6] Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("⚠️  Python 3.8+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def setup_env_file():
    """Setup .env file with API keys."""
    print("\n[2/6] Setting up API keys...")
    
    if os.path.exists('.env'):
        overwrite = input(".env file exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("✅ Using existing .env file")
            return True
    
    print("\nChoose your LLM provider:")
    print("  1. Groq (FREE, Fast) - Recommended")
    print("  2. OpenAI (Premium)")
    print("  3. Mistral AI")
    
    while True:
        choice = input("\nSelect provider (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ Invalid choice")
    
    providers = {
        '1': ('groq', 'GROQ_API_KEY', 'https://console.groq.com/'),
        '2': ('openai', 'OPENAI_API_KEY', 'https://platform.openai.com/'),
        '3': ('mistral', 'MISTRAL_API_KEY', 'https://console.mistral.ai/')
    }
    
    provider_name, key_name, url = providers[choice]
    
    print(f"\n📝 Get your API key from: {url}")
    api_key = input(f"Enter your {provider_name.upper()} API key: ").strip()
    
    # Create .env file
    with open('.env', 'w') as f:
        f.write(f"# {provider_name.upper()} API Key\n")
        f.write(f"{key_name}={api_key}\n")
    
    # Update config.py
    update_config_provider(provider_name)
    
    print(f"✅ API key configured for {provider_name}")
    return True


def update_config_provider(provider):
    """Update provider in config.py."""
    config_path = Path('config.py')
    if not config_path.exists():
        return
    
    content = config_path.read_text()
    
    # Update provider line
    import re
    content = re.sub(
        r'LLM_PROVIDER = "[^"]*"',
        f'LLM_PROVIDER = "{provider}"',
        content
    )
    
    config_path.write_text(content)


def install_dependencies():
    """Install Python dependencies."""
    print("\n[3/6] Installing dependencies...")
    print("This may take a few minutes...\n")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("✅ Dependencies installed")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False


def setup_data_directory():
    """Setup data directory."""
    print("\n[4/6] Setting up data directory...")
    
    os.makedirs('data', exist_ok=True)
    
    # Create memory file
    if not os.path.exists('data/memory.json'):
        with open('data/memory.json', 'w') as f:
            f.write('{}')
    
    # Create user profile
    if not os.path.exists('data/user_profile.json'):
        name = input("What's your name? (optional): ").strip()
        
        profile = {
            "name": name if name else "",
            "language_preference": "en",
            "voice_preference": {
                "tts_voice": "en-IN-NeerjaNeural"
            }
        }
        
        import json
        with open('data/user_profile.json', 'w') as f:
            json.dump(profile, f, indent=2)
    
    print("✅ Data directory configured")
    return True


def test_microphone():
    """Test microphone setup."""
    print("\n[5/6] Testing microphone...")
    
    test = input("Would you like to test your microphone? (Y/n): ").lower()
    if test == 'n':
        print("⚠️  Skipped microphone test")
        return True
    
    try:
        from voice.audio_utils import AudioUtils
        
        mics = AudioUtils.list_microphones()
        print(f"\nFound {len(mics)} microphone(s)")
        
        for idx, name in mics:
            print(f"  [{idx}] {name}")
        
        if AudioUtils.test_microphone():
            print("✅ Microphone working")
            return True
        else:
            print("⚠️  Microphone test inconclusive")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not test microphone: {e}")
        return True


def final_check():
    """Run final verification."""
    print("\n[6/6] Running final check...")
    
    # Check .env exists
    if not os.path.exists('.env'):
        print("❌ .env file missing")
        return False
    
    # Check data directory
    if not os.path.exists('data'):
        print("❌ data directory missing")
        return False
    
    print("✅ Setup complete!")
    return True


def main():
    """Run setup wizard."""
    print_header("JARVIS AI - Setup Wizard")
    
    if not check_python_version():
        return
    
    if not setup_env_file():
        return
    
    if not install_dependencies():
        return
    
    if not setup_data_directory():
        return
    
    test_microphone()
    
    if final_check():
        print_header("Setup Complete! 🎉")
        print("Next steps:")
        print("  1. Review settings in .env file")
        print("  2. Run: python installers/doctor.py (optional check)")
        print("  3. Run: python main.py (start Jarvis)")
        print("\nEnjoy your AI assistant! 🤖")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
