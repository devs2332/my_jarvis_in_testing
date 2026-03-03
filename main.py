#!/usr/bin/env python3
"""
Jarvis AI — Unified Entry Point

This script launches the entire Jarvis AI platform:
  1. Initializes database requirements
  2. Starts the backend FastAPI server
  3. Starts the frontend development server

Usage:
  python main.py              # Launch everything
  python main.py --backend    # Launch backend only
  python main.py --frontend   # Launch frontend only
  python main.py --voice      # Launch voice-only mode (no web server)
"""

import sys
import os
import subprocess
import signal
import time
import argparse
from pathlib import Path

# Ensure the project root is in the Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

# ─── Argument Parser ─────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Jarvis AI — Unified Project Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Launch backend + frontend
  python main.py --backend    Launch backend server only
  python main.py --frontend   Launch frontend dev server only
  python main.py --voice      Launch voice-only mode (original CLI)
        """
    )
    parser.add_argument("--backend", action="store_true", help="Launch backend server only")
    parser.add_argument("--frontend", action="store_true", help="Launch frontend dev server only")
    parser.add_argument("--voice", action="store_true", help="Launch voice-only CLI mode")
    parser.add_argument("--host", default="0.0.0.0", help="Backend server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Backend server port (default: 8000)")
    return parser.parse_args()


# ─── Backend Server ──────────────────────────────────────

def start_backend(host="0.0.0.0", port=8000):
    """Start the FastAPI backend server using uvicorn."""
    print("🚀 Starting Backend Server...")
    return subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "backend.server.app.main:app",
            "--host", host,
            "--port", str(port),
            "--reload"
        ],
        cwd=str(PROJECT_ROOT),
        env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
    )


# ─── Frontend Dev Server ────────────────────────────────

def start_frontend():
    """Start the Vite frontend development server."""
    frontend_dir = PROJECT_ROOT / "frontend"

    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            shell=True,
            check=True,
        )

    print("🎨 Starting Frontend Dev Server...")
    return subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=str(frontend_dir),
        shell=True,
        env={**os.environ},
    )


# ─── Database Initialization ────────────────────────────

def init_database():
    """Ensure database directories and files exist."""
    db_dir = PROJECT_ROOT / "database"
    vector_db_dir = db_dir / "vector_db"

    # Create database directories if they don't exist
    db_dir.mkdir(exist_ok=True)
    vector_db_dir.mkdir(exist_ok=True)

    # Create memory.json if it doesn't exist
    memory_file = db_dir / "memory.json"
    if not memory_file.exists():
        memory_file.write_text("{}")

    print("✅ Database directories initialized")


# ─── Voice-Only Mode ────────────────────────────────────

def start_voice_mode():
    """Launch the original voice-only Jarvis CLI."""
    import queue

    from backend.core.agent import Agent
    from backend.voice.voice_manager import VoiceManager
    from backend.core.hud_server import HUDServer

    try:
        speech_queue = queue.Queue()

        def on_speech_recognized(text):
            speech_queue.put(text)

        voice = VoiceManager()
        jarvis = Agent()
        hud = HUDServer()

        print(f"🤖 {jarvis.state.current_state}: System initialized.")
        hud.start()
        hud.update_state("IDLE", "System Initialized")

        voice.start(on_speech_recognized_callback=on_speech_recognized)
        voice.speak("Jarvis is ready. I am listening.")

        while True:
            hud.update_state("LISTENING", "Listening...")

            try:
                user_input = speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if not user_input or len(user_input) < 2:
                continue

            print("YOU:", user_input)
            hud.update_state("THINKING", user_input)

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


# ─── Main Entry Point ───────────────────────────────────

def main():
    args = parse_args()
    processes = []

    print("=" * 50)
    print("  🤖 JARVIS AI — Platform Launcher")
    print("=" * 50)

    # Initialize database
    init_database()

    # Handle specific mode flags
    if args.voice:
        start_voice_mode()
        return

    if args.backend:
        proc = start_backend(host=args.host, port=args.port)
        processes.append(("Backend", proc))
    elif args.frontend:
        proc = start_frontend()
        processes.append(("Frontend", proc))
    else:
        # Default: launch both backend and frontend
        backend_proc = start_backend(host=args.host, port=args.port)
        processes.append(("Backend", backend_proc))

        # Give the backend a moment to start
        time.sleep(2)

        frontend_proc = start_frontend()
        processes.append(("Frontend", frontend_proc))

    if not processes:
        return

    print("\n" + "=" * 50)
    print("  ✅ All services launched!")
    print("  📋 Press Ctrl+C to stop all services")
    print("=" * 50 + "\n")

    # Graceful shutdown handler
    def shutdown(signum=None, frame=None):
        print("\n\n🛑 Shutting down all services...")
        for name, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"  ✅ {name} stopped")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"  ⚠️  {name} force-killed")
            except Exception as e:
                print(f"  ❌ Error stopping {name}: {e}")
        print("👋 Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Wait for processes
    try:
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n⚠️  {name} exited with code {proc.returncode}")
                    shutdown()
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
