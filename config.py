# jarvis_ai/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

ASSISTANT_NAME = "JARVIS"

# ===== LLM PROVIDER CONFIG =====
# Options: "google", "groq", "mistral", "openrouter", "openai"
LLM_PROVIDER = "groq"   # 👈 switch here

MODEL_GOOGLE = "gemini-1.5-flash"
MODEL_GROQ = "llama-3.1-8b-instant"
MODEL_MISTRAL = "mistral-large-latest"
MODEL_OPENROUTER = "mistralai/mistral-7b-instruct"
MODEL_OPENAI = "gpt-4o-mini"   # fast + cheap

def get_google_api_key(): return os.getenv("GOOGLE_API_KEY")
def get_groq_api_key(): return os.getenv("GROQ_API_KEY")
def get_mistral_api_key(): return os.getenv("MISTRAL_API_KEY")
def get_openrouter_api_key(): return os.getenv("OPENROUTER_API_KEY")
def get_openai_api_key(): return os.getenv("OPENAI_API_KEY")

MEMORY_FILE = "memory.json"
AUTONOMOUS_MODE = "OFF"

# ===== VECTOR DB CONFIG =====
VECTOR_DB_DIR = str(BASE_DIR / "data" / "vector_db")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ===== SERVER CONFIG =====
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

print(f"[DEBUG] Active Provider: {LLM_PROVIDER}")

