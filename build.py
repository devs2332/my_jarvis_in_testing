#!/usr/bin/env python3
"""
Unified Build Script for Jarvis AI

This script handles:
1. Syncing backend configuration to frontend models.json
2. Installing both backend and frontend dependencies
3. Building the frontend for production
4. Preparing output for Cloudflare Workers / Pages
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_REQ_FILE = PROJECT_ROOT / "configuration" / "backend_config" / "requirements.txt"
DIST_DIR = PROJECT_ROOT / "dist"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def run_command(command, cwd=None, exit_on_fail=True):
    """Run a shell command and return its success status."""
    print(f"▶ Running: {' '.join(command) if isinstance(command, list) else command}")
    try:
        result = subprocess.run(
            command,
            cwd=cwd or str(PROJECT_ROOT),
            shell=isinstance(command, str),
            check=exit_on_fail
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if exit_on_fail:
            sys.exit(e.returncode)
        return False
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        if exit_on_fail:
            sys.exit(1)
        return False


def clean_dist():
    """Remove existing dist directory if it exists."""
    if DIST_DIR.exists():
        print("🧹 Cleaning old dist directory...")
        shutil.rmtree(DIST_DIR, ignore_errors=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def init_database():
    """Ensure database directories exist."""
    print("📁 Initializing database directories...")
    db_dir = PROJECT_ROOT / "database"
    vector_db_dir = db_dir / "vector_db"

    db_dir.mkdir(exist_ok=True)
    vector_db_dir.mkdir(exist_ok=True)

    memory_file = db_dir / "memory.json"
    if not memory_file.exists():
        memory_file.write_text("{}")
    print("✅ Database paths ready.")


def build_all():
    print("=" * 50)
    print("  🚀 JARVIS AI — Unified Build Process")
    print("=" * 50)

    # 1. Clean previous builds
    clean_dist()

    # 2. Init DB paths
    init_database()

    # 3. Backend Dependencies
    if BACKEND_REQ_FILE.exists():
        print(f"\n📦 Installing Backend Dependencies...")
        run_command([sys.executable, "-m", "pip", "install", "-r", str(BACKEND_REQ_FILE)])
    else:
        print(f"⚠️ Warning: Backend requirements not found at {BACKEND_REQ_FILE}")

    # 4. Sync Configuration to Frontend
    sync_script = SCRIPTS_DIR / "sync_models.py"
    if sync_script.exists():
        print("\n⚙️  Syncing Model Configuration...")
        run_command([sys.executable, str(sync_script)])
    else:
        print(f"⚠️ Warning: Sync script not found at {sync_script}")

    # 5. Frontend Dependencies
    print("\n📦 Installing Frontend Dependencies...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    run_command([npm_cmd, "install"], cwd=str(FRONTEND_DIR))

    # 6. Build Frontend
    print("\n🔨 Building Frontend...")
    run_command([npm_cmd, "run", "build"], cwd=str(FRONTEND_DIR))

    # 7. Copy assets to root dist (for Cloudflare)
    print("\n📂 Copying build to root dist directory...")
    frontend_dist = FRONTEND_DIR / "dist"
    if frontend_dist.exists():
        shutil.copytree(frontend_dist, DIST_DIR, dirs_exist_ok=True)
        print("✅ Copied successfully.")
    else:
        print(f"❌ Error: Frontend dist directory {frontend_dist} not found. Build may have failed.")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  ✅ Build Complete!")
    print("=" * 50)
    print("\nTo run locally:")
    print("  python main.py")
    print("\nTo deploy to Cloudflare:")
    print("  npx wrangler deploy")
    print("\n")

if __name__ == "__main__":
    build_all()
