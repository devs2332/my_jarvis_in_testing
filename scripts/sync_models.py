import os
import json
import importlib.util
from pathlib import Path

# Paths to the relevant files
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "configuration" / "backend_config" / "config.py"
MODELS_JSON_FILE = PROJECT_ROOT / "frontend" / "src" / "generated" / "models.json"


def load_config(file_path):
    """Dynamically load the config.py module without knowing the package structure."""
    spec = importlib.util.spec_from_file_location("config", file_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def build_active_models(cfg):
    """Build the model list, filtered by ACTIVE_PROVIDERS from config."""
    ACTIVE_PROVIDERS = getattr(cfg, "ACTIVE_PROVIDERS", [])

    # Each provider maps to its config variable and display name.
    provider_map = {
        "openai":     ("MODEL_OPENAI",     "GPT-4o"),
        "google":     ("MODEL_GOOGLE",     "Gemini"),
        "mistral":    ("MODEL_MISTRAL",    "Mistral"),
        "groq":       ("MODEL_GROQ",       "Groq"),
        "openrouter": ("MODEL_OPENROUTER", "OpenRouter"),
        "nvidia":     ("MODEL_NVIDIA",     "NVIDIA"),
    }

    models = []
    for provider in ACTIVE_PROVIDERS:
        entry = provider_map.get(provider)
        if not entry:
            continue
        config_key, display_name = entry
        model_id = getattr(cfg, config_key, None)
        if not model_id:
            continue  # Constant is missing/commented out — skip this provider
        models.append({
            "id": f"{provider}-{model_id}",
            "name": f"{display_name} ({model_id})",
            "provider": provider,
            "model": model_id,
        })
    return models


def sync_models():
    """Reads config, builds active models, and writes to frontend/src/generated/models.json"""
    print("🔄 Syncing models from backend config to frontend...")

    if not CONFIG_FILE.exists():
        print(f"❌ Error: Config file not found at {CONFIG_FILE}")
        return False

    try:
        cfg = load_config(str(CONFIG_FILE))
        active_models = build_active_models(cfg)
        
        # Ensure the generated directory exists
        MODELS_JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to models.json
        with open(MODELS_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(active_models, f, indent=2)

        print(f"✅ Successfully wrote {len(active_models)} models to {MODELS_JSON_FILE.name}")
        for m in active_models:
            print(f"  - {m['name']}")
            
        return True
    
    except Exception as e:
        print(f"❌ Error syncing models: {e}")
        return False

if __name__ == "__main__":
    success = sync_models()
    if not success:
        exit(1)
