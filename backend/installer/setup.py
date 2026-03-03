import os
import shutil
import subprocess
import sys

def install_dependencies():
    print("📦 Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed.")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")

def setup_env():
    print("🔑 Checking .env file...")
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✨ Created .env from .env.example. Please edit it with your API keys.")
        else:
            print("⚠️ .env.example not found. Creating empty .env.")
            with open(".env", "w") as f:
                f.write("# API KEYS\nGROQ_API_KEY=\nOPENAI_API_KEY=\n")
    else:
        print("✅ .env file exists.")

def main():
    print("🚀 Starting Jarvis Setup...")
    setup_env()
    install_dependencies()
    print("🎉 Setup complete! Run 'python installer/doctor.py' to verify.")

if __name__ == "__main__":
    main()
